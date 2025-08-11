import os
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
TOMTOM_API_KEY = os.getenv('TOMTOM_API_KEY')

class TrafficAnalyzer:
    """Class for analyzing traffic conditions using TomTom Traffic APIs"""
    
    def __init__(self, api_key=None):
        """Initialize the TrafficAnalyzer with API key"""
        self.api_key = api_key or TOMTOM_API_KEY
        if not self.api_key:
            raise ValueError("TomTom API key is required")
    
    def get_traffic_flow(self, latitude, longitude):
        """Get traffic flow data for a specific location"""
        url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={latitude},{longitude}&key={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_traffic_incidents(self, min_lat, min_lon, max_lat, max_lon):
        """Get traffic incidents in a bounding box"""
        url = f"https://api.tomtom.com/traffic/services/4/incidentDetails/s3/{min_lon},{min_lat},{max_lon},{max_lat}/10/-1/json?key={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_route_with_traffic(self, origin_lat, origin_lon, dest_lat, dest_lon):
        """Get route between two locations with traffic information"""
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin_lat},{origin_lon}:{dest_lat},{dest_lon}/json?key={self.api_key}&traffic=true&travelMode=car"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def analyze_route_traffic(self, origin_lat, origin_lon, dest_lat, dest_lon):
        """Analyze traffic conditions along a route"""
        # Get route with traffic information
        route_data = self.get_route_with_traffic(origin_lat, origin_lon, dest_lat, dest_lon)
        
        # Extract route points
        route_points = self._extract_route_points(route_data)
        
        # Calculate bounding box for the route
        min_lat = min(point['lat'] for point in route_points)
        min_lon = min(point['lon'] for point in route_points)
        max_lat = max(point['lat'] for point in route_points)
        max_lon = max(point['lon'] for point in route_points)
        
        # Add padding to the bounding box
        padding = 0.05  # approximately 5km
        min_lat -= padding
        min_lon -= padding
        max_lat += padding
        max_lon += padding
        
        # Get traffic incidents in the bounding box
        try:
            incidents_data = self.get_traffic_incidents(min_lat, min_lon, max_lat, max_lon)
            incidents = incidents_data.get('incidents', [])
        except Exception as e:
            print(f"Error getting traffic incidents: {e}")
            incidents = []
        
        # Extract route summary
        route_summary = route_data['routes'][0]['summary']
        travel_time_seconds = route_summary.get('travelTimeInSecondsWithTraffic', route_summary['travelTimeInSeconds'])
        travel_time_without_traffic = route_summary['travelTimeInSeconds']
        distance_meters = route_summary['lengthInMeters']
        
        # Calculate congestion level
        if travel_time_without_traffic > 0:
            congestion_ratio = travel_time_seconds / travel_time_without_traffic
        else:
            congestion_ratio = 1.0
        
        congestion_level = self._classify_congestion_level(congestion_ratio)
        
        # Analyze traffic density at different segments
        density_levels = self._analyze_segment_density(route_data, incidents)
        
        return {
            'route_summary': route_summary,
            'travel_time_seconds': travel_time_seconds,
            'travel_time_without_traffic': travel_time_without_traffic,
            'distance_km': round(distance_meters / 1000, 2),
            'congestion_ratio': congestion_ratio,
            'congestion_level': congestion_level,
            'incidents': incidents,
            'density_levels': density_levels,
            'route_points': route_points
        }
    
    def find_optimal_departure_time(self, origin_lat, origin_lon, dest_lat, dest_lon, target_arrival=None):
        """Find optimal departure time based on traffic patterns"""
        # Generate traffic patterns for different times
        traffic_patterns = self._generate_traffic_patterns()
        
        # Find the time with the least traffic
        optimal_hour = min(traffic_patterns['hourly_data'], key=lambda x: x['congestion_factor'])
        
        # If target arrival is specified, calculate departure time based on that
        if target_arrival:
            try:
                arrival_time = datetime.strptime(target_arrival, "%H:%M")
                travel_time_seconds = self._get_estimated_travel_time(origin_lat, origin_lon, dest_lat, dest_lon)
                departure_time = arrival_time - timedelta(seconds=travel_time_seconds)
                optimal_time = departure_time.strftime("%I:%M %p")
            except Exception as e:
                print(f"Error calculating departure time based on arrival: {e}")
                optimal_time = self._format_hour(optimal_hour['hour'])
        else:
            optimal_time = self._format_hour(optimal_hour['hour'])
        
        return {
            'optimal_departure_time': optimal_time,
            'traffic_patterns': traffic_patterns,
            'congestion_factor': optimal_hour['congestion_factor'],
            'travel_time': optimal_hour['travel_time']
        }
    
    def analyze_traffic_density(self, origin_lat, origin_lon, dest_lat, dest_lon):
        """Analyze traffic density at different segments of a route"""
        # Get route with traffic information
        route_data = self.get_route_with_traffic(origin_lat, origin_lon, dest_lat, dest_lon)
        
        # Extract route points
        route_points = self._extract_route_points(route_data)
        
        # Calculate bounding box for the route
        min_lat = min(point['lat'] for point in route_points)
        min_lon = min(point['lon'] for point in route_points)
        max_lat = max(point['lat'] for point in route_points)
        max_lon = max(point['lon'] for point in route_points)
        
        # Add padding to the bounding box
        padding = 0.05
        min_lat -= padding
        min_lon -= padding
        max_lat += padding
        max_lon += padding
        
        # Get traffic incidents in the bounding box
        try:
            incidents_data = self.get_traffic_incidents(min_lat, min_lon, max_lat, max_lon)
            incidents = incidents_data.get('incidents', [])
        except Exception as e:
            print(f"Error getting traffic incidents: {e}")
            incidents = []
        
        # Analyze traffic density at different segments
        density_levels = self._analyze_segment_density(route_data, incidents)
        
        return {
            'density_levels': density_levels,
            'incidents': incidents,
            'route_points': route_points
        }
    
    def _extract_route_points(self, route_data):
        """Extract route points from TomTom route response"""
        points = []
        legs = route_data['routes'][0]['legs']
        
        for leg in legs:
            for point in leg['points']:
                points.append({
                    'lat': point['latitude'],
                    'lon': point['longitude']
                })
        
        return points
    
    def _classify_congestion_level(self, congestion_ratio):
        """Classify congestion level based on ratio of travel time with traffic to without traffic"""
        if congestion_ratio < 1.1:
            return "Low"
        elif congestion_ratio < 1.3:
            return "Medium"
        else:
            return "High"
    
    def _analyze_segment_density(self, route_data, incidents):
        """Analyze traffic density at different segments of a route"""
        # Extract route summary
        route_summary = route_data['routes'][0]['summary']
        travel_time_seconds = route_summary.get('travelTimeInSecondsWithTraffic', route_summary['travelTimeInSeconds'])
        travel_time_without_traffic = route_summary['travelTimeInSeconds']
        
        # Calculate congestion ratio
        if travel_time_without_traffic > 0:
            congestion_ratio = travel_time_seconds / travel_time_without_traffic
        else:
            congestion_ratio = 1.0
        
        # Determine density levels for different areas based on congestion ratio and incidents
        incident_count = len(incidents)
        
        # Major Intersections: More affected by incidents
        if incident_count > 2 or congestion_ratio > 1.5:
            major_intersections = "High"
        elif incident_count > 0 or congestion_ratio > 1.2:
            major_intersections = "Medium"
        else:
            major_intersections = "Low"
        
        # Highway Segments: Less affected by congestion but more by incidents
        if incident_count > 1 and congestion_ratio > 1.3:
            highway_segments = "High"
        elif incident_count > 0 or congestion_ratio > 1.1:
            highway_segments = "Medium"
        else:
            highway_segments = "Low"
        
        # Urban Streets: More affected by congestion
        if congestion_ratio > 1.4:
            urban_streets = "High"
        elif congestion_ratio > 1.2:
            urban_streets = "Medium"
        else:
            urban_streets = "Low"
        
        return {
            'Major Intersections': major_intersections,
            'Highway Segments': highway_segments,
            'Urban Streets': urban_streets
        }
    
    def _get_estimated_travel_time(self, origin_lat, origin_lon, dest_lat, dest_lon):
        """Get estimated travel time between two points"""
        try:
            route_data = self.get_route_with_traffic(origin_lat, origin_lon, dest_lat, dest_lon)
            return route_data['routes'][0]['summary'].get('travelTimeInSecondsWithTraffic', 
                                                        route_data['routes'][0]['summary']['travelTimeInSeconds'])
        except Exception as e:
            print(f"Error getting travel time: {e}")
            # Fallback: estimate based on distance
            from geopy.distance import geodesic
            origin = (origin_lat, origin_lon)
            destination = (dest_lat, dest_lon)
            distance_km = geodesic(origin, destination).kilometers
            avg_speed_kmh = 40  # Assuming average speed of 40 km/h in Indian traffic
            return int(distance_km / avg_speed_kmh * 3600)  # Convert to seconds
    
    def _generate_traffic_patterns(self, current_hour=None):
        """Generate traffic patterns for different times of day"""
        if current_hour is None:
            current_hour = datetime.now().hour
        
        # Define traffic patterns for different hours (0-23)
        # Higher congestion factor means more traffic
        hourly_patterns = [
            # Late night/early morning (0-5): Low traffic
            {'hour': 0, 'congestion_factor': 0.2, 'travel_time': 'Very Fast'},
            {'hour': 1, 'congestion_factor': 0.1, 'travel_time': 'Very Fast'},
            {'hour': 2, 'congestion_factor': 0.1, 'travel_time': 'Very Fast'},
            {'hour': 3, 'congestion_factor': 0.1, 'travel_time': 'Very Fast'},
            {'hour': 4, 'congestion_factor': 0.2, 'travel_time': 'Very Fast'},
            {'hour': 5, 'congestion_factor': 0.3, 'travel_time': 'Fast'},
            
            # Morning rush (6-9): High traffic
            {'hour': 6, 'congestion_factor': 0.6, 'travel_time': 'Moderate'},
            {'hour': 7, 'congestion_factor': 0.8, 'travel_time': 'Slow'},
            {'hour': 8, 'congestion_factor': 0.9, 'travel_time': 'Very Slow'},
            {'hour': 9, 'congestion_factor': 0.8, 'travel_time': 'Slow'},
            
            # Mid-day (10-15): Moderate traffic
            {'hour': 10, 'congestion_factor': 0.6, 'travel_time': 'Moderate'},
            {'hour': 11, 'congestion_factor': 0.5, 'travel_time': 'Moderate'},
            {'hour': 12, 'congestion_factor': 0.5, 'travel_time': 'Moderate'},
            {'hour': 13, 'congestion_factor': 0.5, 'travel_time': 'Moderate'},
            {'hour': 14, 'congestion_factor': 0.5, 'travel_time': 'Moderate'},
            {'hour': 15, 'congestion_factor': 0.6, 'travel_time': 'Moderate'},
            
            # Evening rush (16-19): High traffic
            {'hour': 16, 'congestion_factor': 0.7, 'travel_time': 'Slow'},
            {'hour': 17, 'congestion_factor': 0.9, 'travel_time': 'Very Slow'},
            {'hour': 18, 'congestion_factor': 1.0, 'travel_time': 'Very Slow'},
            {'hour': 19, 'congestion_factor': 0.8, 'travel_time': 'Slow'},
            
            # Evening (20-23): Decreasing traffic
            {'hour': 20, 'congestion_factor': 0.6, 'travel_time': 'Moderate'},
            {'hour': 21, 'congestion_factor': 0.5, 'travel_time': 'Moderate'},
            {'hour': 22, 'congestion_factor': 0.4, 'travel_time': 'Fast'},
            {'hour': 23, 'congestion_factor': 0.3, 'travel_time': 'Fast'}
        ]
        
        # Add some randomness to make it more realistic
        for pattern in hourly_patterns:
            # Add random variation of ±0.1
            pattern['congestion_factor'] = max(0.1, min(1.0, pattern['congestion_factor'] + (np.random.random() - 0.5) * 0.2))
        
        # Create time series data for visualization
        hours = [pattern['hour'] for pattern in hourly_patterns]
        congestion = [pattern['congestion_factor'] for pattern in hourly_patterns]
        
        # Highlight current hour and next few hours
        highlighted_hours = [(current_hour + i) % 24 for i in range(6)]  # Current hour and next 5 hours
        
        return {
            'hourly_data': hourly_patterns,
            'current_hour': current_hour,
            'highlighted_hours': highlighted_hours,
            'chart_data': {
                'hours': hours,
                'congestion': congestion
            }
        }
    
    def _format_hour(self, hour):
        """Format hour (0-23) to AM/PM format"""
        if hour == 0:
            return "12:00 AM"
        elif hour < 12:
            return f"{hour}:00 AM"
        elif hour == 12:
            return "12:00 PM"
        else:
            return f"{hour-12}:00 PM"

# Example usage
if __name__ == "__main__":
    analyzer = TrafficAnalyzer()
    
    # Example coordinates for Delhi
    delhi_lat, delhi_lon = 28.6139, 77.2090
    
    # Example coordinates for Mumbai
    mumbai_lat, mumbai_lon = 19.0760, 72.8777
    
    # Get traffic flow at a specific location
    try:
        flow_data = analyzer.get_traffic_flow(delhi_lat, delhi_lon)
        print("Traffic Flow Data:", json.dumps(flow_data, indent=2)[:200] + "...")
    except Exception as e:
        print(f"Error getting traffic flow: {e}")
    
    # Analyze route traffic
    try:
        route_analysis = analyzer.analyze_route_traffic(delhi_lat, delhi_lon, mumbai_lat, mumbai_lon)
        print("\nRoute Analysis:")
        print(f"Distance: {route_analysis['distance_km']} km")
        print(f"Travel Time: {route_analysis['travel_time_seconds'] // 60} minutes")
        print(f"Congestion Level: {route_analysis['congestion_level']}")
        print(f"Density Levels: {route_analysis['density_levels']}")
    except Exception as e:
        print(f"Error analyzing route traffic: {e}")
    
    # Find optimal departure time
    try:
        optimal_time = analyzer.find_optimal_departure_time(delhi_lat, delhi_lon, mumbai_lat, mumbai_lon)
        print("\nOptimal Departure Time:", optimal_time['optimal_departure_time'])
    except Exception as e:
        print(f"Error finding optimal departure time: {e}")