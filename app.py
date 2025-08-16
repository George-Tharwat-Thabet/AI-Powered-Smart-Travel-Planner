import os
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
watsonx_available = True
# except ImportError:
#     print("Warning: IBM Watsonx AI not available. AI analysis will be simulated.")
#     watsonx_available = False

# Define AI model training prompt
AI_TRAINING_PROMPT = """
Training prompt for Smart Travel Planner AI Model (IBM Granite 3.3-8b-alora-uncertainty)

You are an AI assistant specialized in analyzing traffic patterns and providing travel recommendations in India.
Your task is to analyze traffic data and provide insights on the following aspects:

1. Traffic Density Classification:
   - Classify traffic density at major intersections, highway segments, and urban streets as Low, Medium, or High
   - For each classification, provide reasoning based on traffic flow data, incidents, and historical patterns

2. Route Optimization:
   - Analyze multiple possible routes between origin and destination
   - Consider factors like current traffic conditions, road quality, and historical congestion patterns
   - Recommend the optimal route with justification

3. Departure Time Recommendation:
   - Analyze traffic patterns throughout the day
   - Identify time periods with minimal congestion
   - Recommend optimal departure times with confidence levels

4. Traffic Incident Analysis:
   - Analyze the impact of current incidents on travel time
   - Predict how long incidents might affect traffic
   - Suggest alternative routes to avoid incident areas

5. Location-Specific Insights:
   - Provide insights specific to Indian cities and regions
   - Consider local traffic patterns, peak hours, and common congestion points
   - Account for seasonal variations and special events

Your responses should be detailed, accurate, and formatted in a way that's easy for travelers to understand.
Use the following HTML structure for your response to match the frontend display:

```html
<p><strong>AI-powered analysis of the route from [ORIGIN] to [DESTINATION]:</strong> 
Our system has analyzed real-time traffic data, including road sensors and satellite imagery, 
to provide the most accurate forecast. Below is a summary of vehicle density across key segments of your journey.</p>

<ul class="density-analysis">
    <li>
        <div class="analysis-item">
            <span class="area-name">Major Intersections</span>
            <p class="area-description">[DESCRIPTION BASED ON DENSITY LEVEL]</p>
        </div>
        <span class="density-value [low/medium/high]">[Low/Medium/High]</span>
    </li>
    <li>
        <div class="analysis-item">
            <span class="area-name">Highway Segments</span>
            <p class="area-description">[DESCRIPTION BASED ON DENSITY LEVEL]</p>
        </div>
        <span class="density-value [low/medium/high]">[Low/Medium/High]</span>
    </li>
    <li>
        <div class="analysis-item">
            <span class="area-name">Urban Streets</span>
            <p class="area-description">[DESCRIPTION BASED ON DENSITY LEVEL]</p>
        </div>
        <span class="density-value [low/medium/high]">[Low/Medium/High]</span>
    </li>
</ul>

<h4>Traffic Incidents</h4>
<ul>
    <li>[INCIDENT DESCRIPTION]</li>
    <!-- Add more incidents if available -->
</ul>

<h4>Recommended Travel Times</h4>
<ul>
    <li>[TIME] - [REASON]</li>
    <!-- Add more recommended times -->
</ul>
```

Example input data structure:
{"origin": "Mumbai, Maharashtra", "destination": "Pune, Maharashtra", "traffic_data": {...}}

Example expected output structure:
{"html_content": "<p>Analysis of route from Mumbai to Pune...</p>", "density_levels": {"Major Intersections": "High", ...}}
"""

# Define fine-tuning dataset structure for the model
AI_FINE_TUNING_STRUCTURE = {
    "dataset_description": "Traffic analysis and route optimization for Indian cities",
    "input_format": {
        "origin": "String - Origin location name",
        "destination": "String - Destination location name",
        "traffic_data": {
            "route_summary": "Object - Summary of route details",
            "incidents": "Array - Traffic incidents along the route",
            "traffic_patterns": "Object - Traffic patterns at different times"
        }
    },
    "output_format": {
        "html_content": "String - HTML formatted analysis for display",
        "density_levels": "Object - Traffic density classifications",
        "optimal_departure": "String - Recommended departure time",
        "confidence_score": "Float - Confidence level of the analysis (0-1)"
    },
    "training_examples": "Minimum 100 diverse examples covering various routes, traffic conditions, and times of day"
}

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='.')
CORS(app)  # Enable CORS for all routes

# Serve static files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# API Keys
TOMTOM_API_KEY = "NMOmmbu9B2Dmtgf9xEvytuvKvrvzXb3U"
IBM_WATSONX_API_KEY = "b5oYyF7lFa1WaEySvmQ6Gre0eMEpYxyuRHIbpP3MtCwP"

# Initialize geocoder
geolocator = Nominatim(user_agent="smart-travel-planner")

# # Initialize IBM Watsonx model if available
# if watsonx_available and IBM_WATSONX_API_KEY:
#     try:
#         # Using IBM Granite 3.3-8b-alora-uncertainty model for improved traffic analysis
#         # This model is specialized for uncertainty quantification and provides confidence scores
#         model = Model(
#             model_id="ibm-granite/granite-3.3-8b-alora-uncertainty",
#             credentials={
#                 "apikey": IBM_WATSONX_API_KEY,
#                 "url": "https://us-south.ml.cloud.ibm.com"
#             },
#             project_id="smart-travel-planner",
#             space_id="smart-travel-planner-space"
#         )
#         print("IBM Granite 3.3-8b-alora-uncertainty model initialized successfully")
#     except Exception as e:
#         print(f"Error initializing IBM Watsonx AI model: {e}")
#         watsonx_available = False

@app.route('/api/geocode', methods=['POST'])
def geocode_location():
    """Convert location name to coordinates"""
    data = request.json
    location = data.get('location')
    
    if not location:
        return jsonify({'error': 'Location is required'}), 400
    
    try:
        # Add India to improve geocoding accuracy
        if 'india' not in location.lower():
            location = f"{location}, India"
            
        location_data = geolocator.geocode(location)
        
        if not location_data:
            return jsonify({'error': 'Location not found'}), 404
            
        return jsonify({
            'location': location,
            'latitude': location_data.latitude,
            'longitude': location_data.longitude,
            'address': location_data.address
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic-flow', methods=['POST'])
def get_traffic_flow():
    """Get traffic flow data for a specific location"""
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not latitude or not longitude:
        return jsonify({'error': 'Latitude and longitude are required'}), 400
    
    try:
        # TomTom Traffic Flow API
        url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={latitude},{longitude}&key={TOMTOM_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic-incidents', methods=['POST'])
def get_traffic_incidents():
    """Get traffic incidents in a bounding box"""
    data = request.json
    min_lat = data.get('min_lat')
    min_lon = data.get('min_lon')
    max_lat = data.get('max_lat')
    max_lon = data.get('max_lon')
    
    if not all([min_lat, min_lon, max_lat, max_lon]):
        return jsonify({'error': 'All bounding box coordinates are required'}), 400
    
    try:
        # TomTom Traffic Incidents API
        url = f"https://api.tomtom.com/traffic/services/4/incidentDetails/s3/{min_lon},{min_lat},{max_lon},{max_lat}/10/-1/json?key={TOMTOM_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/route', methods=['POST'])
def get_route():
    """Get route between two locations with traffic information"""
    data = request.json
    origin_lat = data.get('origin_lat')
    origin_lon = data.get('origin_lon')
    dest_lat = data.get('dest_lat')
    dest_lon = data.get('dest_lon')
    
    if not all([origin_lat, origin_lon, dest_lat, dest_lon]):
        return jsonify({'error': 'Origin and destination coordinates are required'}), 400
    
    try:
        # TomTom Routing API with traffic information
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin_lat},{origin_lon}:{dest_lat},{dest_lon}/json?key={TOMTOM_API_KEY}&traffic=true&travelMode=car"
        response = requests.get(url)
        response.raise_for_status()
        route_data = response.json()
        
        # Extract relevant information
        route_summary = route_data['routes'][0]['summary']
        travel_time_seconds = route_summary['travelTimeInSeconds']
        travel_time_with_traffic_seconds = route_summary.get('travelTimeInSecondsWithTraffic', travel_time_seconds)
        distance_meters = route_summary['lengthInMeters']
        
        # Format travel time
        travel_time = format_time(travel_time_with_traffic_seconds)
        
        # Get route points for map display
        route_points = extract_route_points(route_data)
        
        return jsonify({
            'travel_time': travel_time,
            'travel_time_seconds': travel_time_with_traffic_seconds,
            'distance_km': round(distance_meters / 1000, 2),
            'route_points': route_points,
            'full_route': route_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic-stats', methods=['POST'])
def get_traffic_stats():
    """Get historical traffic statistics for route analysis"""
    data = request.json
    origin_lat = data.get('origin_lat')
    origin_lon = data.get('origin_lon')
    dest_lat = data.get('dest_lat')
    dest_lon = data.get('dest_lon')
    
    if not all([origin_lat, origin_lon, dest_lat, dest_lon]):
        return jsonify({'error': 'Origin and destination coordinates are required'}), 400
    
    try:
        # TomTom Traffic Stats API - Route Analysis
        # Note: This is a premium API and might require additional authentication
        url = f"https://api.tomtom.com/traffic/services/4/routeStats/{origin_lat},{origin_lon}:{dest_lat},{dest_lon}/json?key={TOMTOM_API_KEY}"
        
        # This API might not be accessible with the provided key
        # Simulating response for demonstration
        # In a production environment, you would use the actual API
        
        # Simulate traffic patterns for different times of day
        current_hour = datetime.now().hour
        traffic_patterns = generate_traffic_patterns(current_hour)
        
        return jsonify(traffic_patterns)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/optimal-departure', methods=['POST'])
def get_optimal_departure():
    """Get optimal departure time based on traffic analysis"""
    data = request.json
    origin_lat = data.get('origin_lat')
    origin_lon = data.get('origin_lon')
    dest_lat = data.get('dest_lat')
    dest_lon = data.get('dest_lon')
    target_arrival = data.get('target_arrival')  # Optional: target arrival time
    
    if not all([origin_lat, origin_lon, dest_lat, dest_lon]):
        return jsonify({'error': 'Origin and destination coordinates are required'}), 400
    
    try:
        # Generate traffic patterns for different times
        traffic_patterns = generate_traffic_patterns()
        
        # Find the time with the least traffic
        optimal_hour = min(traffic_patterns['hourly_data'], key=lambda x: x['congestion_factor'])
        
        # Format the optimal departure time
        optimal_time = format_hour(optimal_hour['hour'])
        
        # If target arrival is specified, calculate departure time based on that
        if target_arrival:
            try:
                arrival_time = datetime.strptime(target_arrival, "%H:%M")
                travel_time_seconds = get_estimated_travel_time(origin_lat, origin_lon, dest_lat, dest_lon)
                departure_time = arrival_time - timedelta(seconds=travel_time_seconds)
                optimal_time = departure_time.strftime("%I:%M %p")
            except Exception as e:
                print(f"Error calculating departure time based on arrival: {e}")
        
        return jsonify({
            'optimal_departure_time': optimal_time,
            'traffic_patterns': traffic_patterns,
            'congestion_factor': optimal_hour['congestion_factor'],
            'travel_time': optimal_hour['travel_time']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-analysis', methods=['POST'])
def get_ai_analysis():
    """Get AI-powered analysis of traffic conditions"""
    data = request.json
    origin = data.get('origin')
    destination = data.get('destination')
    origin_lat = data.get('origin_lat')
    origin_lon = data.get('origin_lon')
    dest_lat = data.get('dest_lat')
    dest_lon = data.get('dest_lon')
    
    if not all([origin, destination, origin_lat, origin_lon, dest_lat, dest_lon]):
        return jsonify({'error': 'Origin, destination, and coordinates are required'}), 400
    
    # try:
        # Get traffic data for the route
    traffic_data = get_route_traffic_data(origin_lat, origin_lon, dest_lat, dest_lon)
    
    # Generate AI analysis using IBM Watsonx or simulation
    analysis = generate_ai_analysis(origin, destination, traffic_data)
    
    return jsonify(analysis)
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500

@app.route('/api/plan-trip', methods=['POST'])
def plan_trip():
    """Main endpoint to plan a trip with all necessary information"""
    print("\n[TRIP PLAN] Received trip planning request")
    try:
        data = request.get_json()
        origin = data['origin']
        destination = data['destination']
        preferred_date = data.get('preferred_date', datetime.now().strftime('%Y-%m-%d'))
        preferred_time = data.get('preferred_time', '09:00')
        route_preference = data.get('route_preference', 'fastest')
        
        if not origin or not destination:
            return jsonify({'error': 'Origin and destination are required'}), 400
        # Step 1: Geocode origin and destination
        origin_geocode = geolocator.geocode(f"{origin}, India")
        dest_geocode = geolocator.geocode(f"{destination}, India")
        
        if not origin_geocode or not dest_geocode:
            return jsonify({'error': 'Could not geocode one or both locations'}), 404
        
        origin_lat, origin_lon = origin_geocode.latitude, origin_geocode.longitude
        dest_lat, dest_lon = dest_geocode.latitude, dest_geocode.longitude
        
        # Step 2: Get route information
        route_url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin_lat},{origin_lon}:{dest_lat},{dest_lon}/json?key={TOMTOM_API_KEY}&traffic=true&travelMode=car"
        route_response = requests.get(route_url)
        route_response.raise_for_status()
        route_data = route_response.json()
        
        # Extract route summary
        route_summary = route_data['routes'][0]['summary']
        travel_time_seconds = route_summary.get('travelTimeInSecondsWithTraffic', route_summary['travelTimeInSeconds'])
        distance_km = round(route_summary['lengthInMeters'] / 1000, 2)
        
        # Step 3: Get traffic incidents along the route
        # Calculate bounding box that covers the route
        route_points = extract_route_points(route_data)
        min_lat = min(point['lat'] for point in route_points)
        min_lon = min(point['lon'] for point in route_points)
        max_lat = max(point['lat'] for point in route_points)
        max_lon = max(point['lon'] for point in route_points)
        
        # Add some padding to the bounding box
        padding = 0.05  # approximately 5km
        min_lat -= padding
        min_lon -= padding
        max_lat += padding
        max_lon += padding
        
        incidents_url = f"https://api.tomtom.com/traffic/services/4/incidentDetails/s3/{min_lon},{min_lat},{max_lon},{max_lat}/10/-1/json?key={TOMTOM_API_KEY}"
        incidents_response = requests.get(incidents_url)
        incidents_data = {}
        
        if incidents_response.status_code == 200:
            incidents_data = incidents_response.json()
        
        # Step 4: Get optimal departure time
        traffic_patterns = generate_traffic_patterns()
        optimal_hour = min(traffic_patterns['hourly_data'], key=lambda x: x['congestion_factor'])
        optimal_time = format_hour(optimal_hour['hour'])
        
        # Generate optimal timing based on route preference
        optimal_timing = generate_optimal_timing(origin, destination, preferred_date, preferred_time, route_preference)
        
        # Step 5: Generate AI analysis
        traffic_data = {
            'route_summary': route_summary,
            'incidents': incidents_data.get('incidents', []),
            'traffic_patterns': traffic_patterns
        }
        
        ai_analysis = generate_ai_analysis(origin, destination, traffic_data, route_preference)
        
        # Format the best route description
        best_route = format_route_description(route_data, origin, destination)
        
        # Prepare the response
        response_data = {
            'bestRoute': best_route,
            'departureTime': optimal_time,
            'travelTime': format_time(travel_time_seconds),
            'distance': f"{distance_km} km",
            'aiAnalysis': ai_analysis['html_content'],
            'routePoints': route_points,
            'trafficIncidents': incidents_data.get('incidents', []),
            'trafficPatterns': traffic_patterns,
            'densityLevels': ai_analysis['density_levels'],
            'aiSource': ai_analysis.get('source', 'unknown'),
            'aiModel': ai_analysis.get('model', 'none'),
            'aiTimestamp': ai_analysis.get('timestamp', ''),
            'optimalTiming': optimal_timing
        }
        
        # Log the AI analysis source
        print(f"[TRIP PLAN] AI Analysis Source: {ai_analysis.get('source', 'unknown')}")
        if ai_analysis.get('source') == 'simulation':
            print("[TRIP PLAN] WARNING: Using simulated AI analysis instead of real IBM Watsonx AI")
        else:
            print(f"[TRIP PLAN] Using real AI analysis from {ai_analysis.get('model', 'unknown model')}")
        
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper functions
def format_time(seconds):
    """Format seconds into a readable time string"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"

def format_hour(hour):
    """Format hour (0-23) to AM/PM format"""
    if hour == 0:
        return "12:00 AM"
    elif hour < 12:
        return f"{hour}:00 AM"
    elif hour == 12:
        return "12:00 PM"
    else:
        return f"{hour-12}:00 PM"

def extract_route_points(route_data):
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

def get_estimated_travel_time(origin_lat, origin_lon, dest_lat, dest_lon):
    """Get estimated travel time between two points"""
    try:
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin_lat},{origin_lon}:{dest_lat},{dest_lon}/json?key={TOMTOM_API_KEY}&traffic=true"
        response = requests.get(url)
        response.raise_for_status()
        route_data = response.json()
        
        return route_data['routes'][0]['summary'].get('travelTimeInSecondsWithTraffic', 
                                                     route_data['routes'][0]['summary']['travelTimeInSeconds'])
    except Exception as e:
        print(f"Error getting travel time: {e}")
        # Fallback: estimate based on distance and average speed
        origin = (origin_lat, origin_lon)
        destination = (dest_lat, dest_lon)
        distance_km = geodesic(origin, destination).kilometers
        avg_speed_kmh = 40  # Assuming average speed of 40 km/h in Indian traffic
        return int(distance_km / avg_speed_kmh * 3600)  # Convert to seconds

def get_route_traffic_data(origin_lat, origin_lon, dest_lat, dest_lon):
    """Get traffic data for a route"""
    try:
        # Get route information
        route_url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin_lat},{origin_lon}:{dest_lat},{dest_lon}/json?key={TOMTOM_API_KEY}&traffic=true&travelMode=car"
        route_response = requests.get(route_url)
        route_response.raise_for_status()
        route_data = route_response.json()

        # Get traffic incidents along the route
        route_points = extract_route_points(route_data)
        min_lat = min(point['lat'] for point in route_points)
        min_lon = min(point['lon'] for point in route_points)
        max_lat = max(point['lat'] for point in route_points)
        max_lon = max(point['lon'] for point in route_points)

        # Add some padding to the bounding box
        padding = 0.05
        min_lat -= padding
        min_lon -= padding
        max_lat += padding
        max_lon += padding

        incidents_url = f"https://api.tomtom.com/traffic/services/4/incidentDetails/s3/{min_lon},{min_lat},{max_lon},{max_lat}/10/-1/json?key={TOMTOM_API_KEY}"
        incidents_response = requests.get(incidents_url)
        incidents_data = {}

        if incidents_response.status_code == 200:
            incidents_data = incidents_response.json()

        # Combine data
        return {
            'route_summary': route_data['routes'][0]['summary'],
            'incidents': incidents_data.get('incidents', []),
            'traffic_patterns': generate_traffic_patterns()
        }
    except Exception as e:
        print(f"Error getting route traffic data: {e}")
        return {
            'route_summary': {},
            'incidents': [],
            'traffic_patterns': generate_traffic_patterns()
        }

def get_route_traffic_data_from_route(route_data):
    """Extract traffic data from route data structure"""
    try:
        return {
            'travel_time_seconds': route_data['travel_time_seconds'],
            'travel_time_without_traffic': route_data['travel_time_without_traffic'],
            'distance_meters': int(route_data['distance_km'] * 1000),
            'traffic_density': route_data['traffic_density'],
            'emissions_estimate': route_data['emissions_estimate'],
            'scenic_rating': route_data['scenic_rating']
        }
    except Exception as e:
        print(f"Error extracting route traffic data: {e}")
        return {}

def generate_traffic_patterns(current_hour=None):
    """Generate simulated traffic patterns for different times of day"""
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
    current_index = current_hour
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

def generate_ai_analysis(origin, destination, traffic_data, route_preference='fastest'):
    """Generate AI analysis of traffic conditions using IBM Watsonx or simulation"""
    print(f"\n[AI ANALYSIS] Generating analysis for route: {origin} to {destination}")
    print(f"[AI ANALYSIS] Watsonx available: {watsonx_available}")
    print(f"[AI ANALYSIS] Route preference: {route_preference}")
    print(f"[AI ANALYSIS] Model loaded: {'model' in globals()}")

    
    
    if True :
        try:
            print(f"[AI ANALYSIS] Using IBM Watsonx AI for traffic analysis")
            # Prepare prompt for the AI model using the training prompt as a base
            system_prompt = AI_TRAINING_PROMPT
            
            incidents_text = ""
            if traffic_data.get('incidents'):
                incidents_text = "\nTraffic incidents along the route:\n"
                for i, incident in enumerate(traffic_data['incidents'][:5]):  # Limit to 5 incidents
                    incidents_text += f"- {incident.get('description', 'Unknown incident')}\n"
            
            route_summary = traffic_data.get('route_summary', {})
            travel_time = format_time(route_summary.get('travelTimeInSecondsWithTraffic', 0))
            distance = round(route_summary.get('lengthInMeters', 0) / 1000, 2)
            
            user_prompt = f"""Analyze traffic conditions for a route from {origin} to {destination} in India.
            
            Route preference: {route_preference}
            Route information:
            - Distance: {distance} km
            - Estimated travel time with current traffic: {travel_time}
            {incidents_text}
            
            Current Time: {datetime.now().strftime('%H:%M')}
            Day of Week: {datetime.now().strftime('%A')}
            
            Based on this information and route preference, provide a detailed analysis of the traffic conditions along this route. 
            Include information about congestion levels at major intersections, highway segments, and urban streets. 
            Classify each area as having Low, Medium, or High vehicle density.
            Also suggest the best times to travel this route to avoid traffic congestion, considering the {route_preference} preference.
            Format your response as HTML that can be directly displayed on a website.
            """
            
            # Combine system prompt and user prompt
            full_prompt = f"{system_prompt}\n\nUser Request:\n{user_prompt}"
            
            # # Generate response from the AI model with improved parameters for the Granite model
            # params = {
            #     GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
            #     GenParams.MAX_NEW_TOKENS: 800,  # Increased token limit for more detailed analysis
            #     GenParams.MIN_NEW_TOKENS: 200,
            #     GenParams.TEMPERATURE: 0.5,     # Lower temperature for more focused responses
            #     GenParams.TOP_P: 0.9,           # Added top_p parameter for better text quality
            #     GenParams.REPETITION_PENALTY: 1.1  # Added to reduce repetition in responses
            # }
            
            # print(f"[AI ANALYSIS] Sending prompt to IBM Watsonx AI model")
            # print(f"[AI ANALYSIS] Prompt length: {len(full_prompt)} characters")
            
            # response = model.generate(prompt=full_prompt, params=params)
            # ai_content = response.generated_text

            import requests

            url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"

            body = {
            "messages": [{"role":"system",
                            "content":"""You always answer the questions with markdown formatting using GitHub syntax. 
                            The markdown formatting you support: headings, bold, italic, links, tables, lists, code blocks, and blockquotes. 
                            You must omit that you answer the questions with markdown.
                            \n\nAny HTML tags must be wrapped in block quotes, for example ```<html>```.
                            You will be penalized for not rendering code in block quotes.
                            \n\nWhen returning code blocks, specify language.
                            \n\nYou are a helpful, respectful and honest assistant. 
                            Always answer as helpfully as possible, while being safe. 
                            \nYour answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content.
                            Please ensure that your responses are socially unbiased and positive in nature.
                            \n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct.
                            If you don'\''t know the answer to a question, please don'\''t share false information."""},
                            {"role":"user","content":[{"type":"text","text":full_prompt}]}],
            "project_id": "6384f8f4-0e9f-451e-8752-dd5267d735be",
            "model_id": "meta-llama/llama-3-3-70b-instruct",
            "frequency_penalty": 0,
            "max_tokens": 2000,
            "presence_penalty": 0,
            "temperature": 0,
            "top_p": 1
            }

            access_token = "eyJraWQiOiIyMDE5MDcyNCIsImFsZyI6IlJTMjU2In0.eyJpYW1faWQiOiJJQk1pZC02OTQwMDBJWDQ5IiwiaWQiOiJJQk1pZC02OTQwMDBJWDQ5IiwicmVhbG1pZCI6IklCTWlkIiwianRpIjoiYmM4YjU2MjctNzdmOC00NmJhLTk1ZDAtNThlMGMxZmY0MTUyIiwiaWRlbnRpZmllciI6IjY5NDAwMElYNDkiLCJnaXZlbl9uYW1lIjoiR2VvcmdlIiwiZmFtaWx5X25hbWUiOiJUaGFyd2F0IiwibmFtZSI6Ikdlb3JnZSBUaGFyd2F0IiwiZW1haWwiOiJnZW9yZ2V0aGFyd2F0Lm9mZmljaWFsQGdtYWlsLmNvbSIsInN1YiI6Imdlb3JnZXRoYXJ3YXQub2ZmaWNpYWxAZ21haWwuY29tIiwiYXV0aG4iOnsic3ViIjoiZ2VvcmdldGhhcndhdC5vZmZpY2lhbEBnbWFpbC5jb20iLCJpYW1faWQiOiJJQk1pZC02OTQwMDBJWDQ5IiwibmFtZSI6Ikdlb3JnZSBUaGFyd2F0IiwiZ2l2ZW5fbmFtZSI6Ikdlb3JnZSIsImZhbWlseV9uYW1lIjoiVGhhcndhdCIsImVtYWlsIjoiZ2VvcmdldGhhcndhdC5vZmZpY2lhbEBnbWFpbC5jb20ifSwiYWNjb3VudCI6eyJ2YWxpZCI6dHJ1ZSwiYnNzIjoiNTI0MDE1YzVjY2RhNDRmMGIzYTQ4YTcxMTQwMjk2NTQiLCJpbXNfdXNlcl9pZCI6IjE0Mjg3NzgzIiwiZnJvemVuIjp0cnVlLCJpbXMiOiIzMDAwODIwIn0sImlhdCI6MTc1NTExMDc0OCwiZXhwIjoxNzU1MTE0MzQ4LCJpc3MiOiJodHRwczovL2lhbS5jbG91ZC5pYm0uY29tL2lkZW50aXR5IiwiZ3JhbnRfdHlwZSI6InVybjppYm06cGFyYW1zOm9hdXRoOmdyYW50LXR5cGU6YXBpa2V5Iiwic2NvcGUiOiJpYm0gb3BlbmlkIiwiY2xpZW50X2lkIjoiZGVmYXVsdCIsImFjciI6MSwiYW1yIjpbInB3ZCJdfQ.OJs5AHsUDQgz1Mz6-RsI_qbiLgOMsq-W02xxqRtmtNIa7rOkzfbDpfxu8mKDh3Gpj8MIoY6UVrCGnOetKtOwyca0WmhR3BWQCRhtwx2i03KPDOUStMZUkn5dbnMUxTgr6Mdqp5uabv10RsaPJ1xCkryNdqCuYOvYR77jJBblke9EdUj4jPBp-2P2S_w3WHo7HgTi_1eQymIjeYauWkNcQI3l7JoQQyh0JuMi3S_GJao_uy_40EBRSXDtiKSAEkZbKcteF6hAnudKRs6esVXbpDQF7qHIMur0nOIMELc0GB-gbRSLVOQQqVCDSaGj418sGNDep591rl2bZYIaU_TfJQ"

            headers = { 
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer"+" "+access_token
            }

            response = requests.post(
            url,
            headers=headers,
            json=body
            )

            if response.status_code != 200:
                raise Exception("Non-200 response: " + str(response.text))

            ai_response = response.json()
            ai_content = ai_response['choices'][0]['message']['content']
            
            print(f"[AI ANALYSIS] Received response from IBM Watsonx AI")
            print(f"[AI ANALYSIS] Response length: {len(ai_content)} characters")
            
            # Extract density levels from the AI response
            density_levels = extract_density_levels(ai_content)
            
            print(f"[AI ANALYSIS] Extracted density levels: {density_levels}")
            print(f"[AI ANALYSIS] Successfully generated AI analysis using IBM Watsonx")
            
            return {
                'html_content': ai_content,
                'density_levels': density_levels,
                'source': 'ibm_watsonx',
                'model': 'granite-3.3-8b-alora-uncertainty',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[AI ANALYSIS] Error generating AI analysis with IBM Watsonx: {e}")
            print(f"[AI ANALYSIS] Falling back to simulated analysis")
            # Fall back to simulated analysis
            return simulate_ai_analysis(origin, destination, traffic_data, route_preference)
    else:
        # If Watsonx is not available, use simulated analysis
        print(f"[AI ANALYSIS] IBM Watsonx AI not available, using simulated analysis")
        return simulate_ai_analysis(origin, destination, traffic_data, route_preference)

def simulate_ai_analysis(origin, destination, traffic_data, route_preference='fastest'):
    """Simulate AI analysis when IBM Watsonx is not available"""
    print(f"[AI ANALYSIS] Simulating AI analysis for route: {origin} to {destination}")
    print(f"[AI ANALYSIS] Route preference: {route_preference}")
    
    # Determine traffic density levels based on traffic data and route preference
    route_summary = traffic_data.get('route_summary', {})
    incidents = traffic_data.get('incidents', [])
    traffic_patterns = traffic_data.get('traffic_patterns', generate_traffic_patterns())
    
    print(f"[AI ANALYSIS] Using simulated data with {len(incidents)} incidents")
    
    # Route preference-based adjustments
    route_adjustments = {
        'fastest': {'intersection_factor': 1.2, 'highway_factor': 0.8, 'urban_factor': 1.0},
        'eco-friendly': {'intersection_factor': 0.9, 'highway_factor': 1.0, 'urban_factor': 0.8},
        'low-traffic': {'intersection_factor': 0.7, 'highway_factor': 0.9, 'urban_factor': 0.6},
        'scenic': {'intersection_factor': 1.0, 'highway_factor': 1.1, 'urban_factor': 1.2}
    }
    
    adjustments = route_adjustments.get(route_preference, route_adjustments['fastest'])
    
    # Determine overall congestion level
    current_hour = datetime.now().hour
    current_pattern = next((p for p in traffic_patterns['hourly_data'] if p['hour'] == current_hour), 
                          {'congestion_factor': 0.5})
    congestion_factor = current_pattern['congestion_factor']
    
    # Determine density levels for different areas with route preference adjustments
    density_levels = {
        'Major Intersections': 'High' if congestion_factor * adjustments['intersection_factor'] > 0.7 else ('Medium' if congestion_factor * adjustments['intersection_factor'] > 0.4 else 'Low'),
        'Highway Segments': 'Medium' if congestion_factor * adjustments['highway_factor'] > 0.6 else ('Low' if congestion_factor * adjustments['highway_factor'] > 0.3 else 'Low'),
        'Urban Streets': 'High' if congestion_factor * adjustments['urban_factor'] > 0.6 else ('Medium' if congestion_factor * adjustments['urban_factor'] > 0.3 else 'Low')
    }
    
    # Route preference descriptions
    route_descriptions = {
        'fastest': 'optimized for minimal travel time',
        'eco-friendly': 'optimized for fuel efficiency and lower emissions',
        'low-traffic': 'avoiding high-traffic areas',
        'scenic': 'featuring pleasant views and interesting landmarks'
    }
    
    # Generate HTML content with route preference
    incident_html = ""
    if incidents:
        incident_html = "<h4>Traffic Incidents</h4><ul>"
        for incident in incidents[:3]:  # Limit to 3 incidents
            incident_html += f"<li>{incident.get('description', 'Unknown incident')}</li>"
        incident_html += "</ul>"
    
    # Route-specific time recommendations
    time_recommendations = {
        'fastest': ['6:00 AM', '7:30 AM', '10:30 AM', '2:00 PM'],
        'eco-friendly': ['8:30 AM', '11:00 AM', '2:30 PM', '9:00 PM'],
        'low-traffic': ['6:30 AM', '11:30 AM', '2:30 PM', '8:30 PM'],
        'scenic': ['7:00 AM', '9:00 AM', '4:00 PM', '6:00 PM']
    }
    
    recommended_times = time_recommendations.get(route_preference, ['8:00 AM', '10:00 AM', '2:00 PM', '6:00 PM'])
    
    optimal_times_html = f"<h4>Recommended Travel Times for {route_preference} Route</h4><ul>"
    for time in recommended_times:
        optimal_times_html += f"<li>{time} - Optimal for {route_preference} travel</li>"
    optimal_times_html += "</ul>"
    
    html_content = f"""
    <p><strong>AI-powered analysis of the route from {origin} to {destination}:</strong> 
    This analysis is specifically tailored for your <strong>{route_preference}</strong> route preference ({route_descriptions.get(route_preference, 'standard route')}).
    Our system has analyzed real-time traffic data, including road sensors and satellite imagery, 
    to provide the most accurate forecast. Below is a summary of vehicle density across key segments of your journey.</p>
    
    <ul class="density-analysis">
    """
    
    # Add density analysis for each area with route-specific insights
    for area, level in density_levels.items():
        level_class = level.lower()
        description = ""
        if level == 'Low':
            if route_preference == 'scenic':
                description = "Excellent for scenic driving with minimal congestion."
            elif route_preference == 'eco-friendly':
                description = "Optimal for fuel-efficient driving with consistent speeds."
            else:
                description = "Expect smooth travel through these areas with minimal congestion."
        elif level == 'Medium':
            if route_preference == 'low-traffic':
                description = "Moderate traffic, but still better than high-congestion routes."
            elif route_preference == 'fastest':
                description = "Minor delays possible, but overall good travel time."
            else:
                description = "Minor delays are possible due to moderate traffic flow."
        else:  # High
            if route_preference == 'fastest':
                description = "Significant delays likely; consider alternative departure times for faster travel."
            elif route_preference == 'low-traffic':
                description = "High congestion - this route may not be optimal for avoiding traffic."
            else:
                description = "Significant delays are likely; consider alternative routes if possible."
        
        html_content += f"""
        <li>
            <div class="analysis-item">
                <span class="area-name">{area}</span>
                <p class="area-description">{description}</p>
            </div>
            <span class="density-value {level_class}">{level}</span>
        </li>
        """
    
    html_content += f"</ul>{incident_html}{optimal_times_html}"
    
    print(f"[AI ANALYSIS] Generated simulated analysis with density levels: {density_levels}")
    
    return {
        'html_content': html_content,
        'density_levels': density_levels,
        'source': 'simulation',
        'timestamp': datetime.now().isoformat(),
        'route_preference': route_preference
    }

def extract_density_levels(ai_content):
    """Extract density levels from AI-generated content"""
    # Default density levels in case extraction fails
    default_levels = {
        'Major Intersections': 'Medium',
        'Highway Segments': 'Low',
        'Urban Streets': 'High'
    }
    
    try:
        # Look for patterns like "Area: Level" or "Area - Level"
        import re
        patterns = [
            r'(Major Intersections|Highway Segments|Urban Streets)[:\s-]\s*(Low|Medium|High)',
            r'(Major Intersections|Highway Segments|Urban Streets).*?(Low|Medium|High)\s*density',
            r'(Low|Medium|High)\s*density.*?(Major Intersections|Highway Segments|Urban Streets)'
        ]
        
        extracted_levels = {}
        
        for pattern in patterns:
            matches = re.findall(pattern, ai_content, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    area = match[0] if match[0] in default_levels else match[1]
                    level = match[1] if match[1] in ['Low', 'Medium', 'High'] else match[0]
                    
                    if area in default_levels and level in ['Low', 'Medium', 'High']:
                        extracted_levels[area] = level
        
        # If we found at least one level, return the extracted levels with defaults for missing areas
        if extracted_levels:
            for area in default_levels:
                if area not in extracted_levels:
                    extracted_levels[area] = default_levels[area]
            return extracted_levels
        else:
            return default_levels
    except Exception as e:
        print(f"Error extracting density levels: {e}")
        return default_levels

def format_route_description(route_data, origin, destination):
    """Format a human-readable route description"""
    try:
        # Extract major roads from the route
        major_roads = []
        for leg in route_data['routes'][0]['legs']:
            for instruction in leg.get('guidance', {}).get('instructions', []):
                road_name = instruction.get('roadNumbers', [])
                if road_name and road_name[0] not in major_roads:
                    major_roads.append(road_name[0])
        
        # Limit to 3 major roads
        major_roads = major_roads[:3]
        
        if major_roads:
            road_text = " → ".join(major_roads)
            return f"{origin} → {road_text} → {destination}"
        else:
            return f"{origin} → {destination}"
    except Exception as e:
        print(f"Error formatting route description: {e}")
        return f"{origin} → {destination}"

def generate_optimal_timing(origin, destination, preferred_date, preferred_time, route_preference):
    """
    Generate optimal timing recommendations based on route preference
    """
    
    # Parse preferred date and time
    try:
        if preferred_date:
            date_obj = datetime.strptime(preferred_date, '%Y-%m-%d')
        else:
            date_obj = datetime.now()
            
        if preferred_time:
            time_parts = preferred_time.split(':')
            preferred_hour = int(time_parts[0])
        else:
            preferred_hour = 8
    except:
        date_obj = datetime.now()
        preferred_hour = 8
    
    # Generate timing recommendations based on route preference
    recommendation = ''
    alternatives = []
    
    switcher = {
        'fastest': {
            'recommendation': 'For the fastest route, avoid peak hours (7-10 AM and 5-8 PM) when traffic is heaviest.',
            'alternatives': [
                {'time': '6:00 AM', 'description': 'Early morning departure - minimal traffic, fastest travel time', 'rating': 'optimal'},
                {'time': '10:30 AM', 'description': 'Mid-morning - light traffic, good travel conditions', 'rating': 'good'},
                {'time': '2:00 PM', 'description': 'Early afternoon - moderate traffic, decent travel time', 'rating': 'good'},
                {'time': '8:00 AM', 'description': 'Peak morning rush - heavy traffic, longer travel time', 'rating': 'avoid'}
            ]
        },
        'eco-friendly': {
            'recommendation': 'For an eco-friendly route with lower emissions, travel during off-peak hours when engines run more efficiently.',
            'alternatives': [
                {'time': '9:30 AM', 'description': 'Post rush hour - steady traffic flow, better fuel efficiency', 'rating': 'optimal'},
                {'time': '2:30 PM', 'description': 'Afternoon travel - consistent speeds, lower emissions', 'rating': 'optimal'},
                {'time': '11:00 PM', 'description': 'Late night - free-flowing traffic, minimal stops', 'rating': 'good'},
                {'time': '7:30 AM', 'description': 'Rush hour - stop-and-go traffic increases emissions', 'rating': 'avoid'}
            ]
        },
        'low-traffic': {
            'recommendation': 'To avoid traffic congestion, plan your departure outside of peak commuting hours.',
            'alternatives': [
                {'time': '5:30 AM', 'description': 'Very early departure - roads are clear, no congestion', 'rating': 'optimal'},
                {'time': '11:00 AM', 'description': 'Late morning - traffic has cleared, smooth journey', 'rating': 'optimal'},
                {'time': '9:00 PM', 'description': 'Evening departure - rush hour has ended', 'rating': 'good'},
                {'time': '6:00 PM', 'description': 'Evening rush hour - expect heavy congestion', 'rating': 'avoid'}
            ]
        },
        'scenic': {
            'recommendation': 'For a scenic route, travel during daylight hours to enjoy the views. Golden hours provide the best lighting.',
            'alternatives': [
                {'time': '7:00 AM', 'description': 'Golden hour departure - beautiful sunrise views along the route', 'rating': 'optimal'},
                {'time': '4:00 PM', 'description': 'Afternoon departure - good lighting for scenic photography', 'rating': 'optimal'},
                {'time': '11:00 AM', 'description': 'Mid-morning - clear visibility, pleasant weather', 'rating': 'good'},
                {'time': '9:00 PM', 'description': 'Night travel - limited scenic visibility', 'rating': 'avoid'}
            ]
        }
    }
    
    # Get recommendations based on route preference
    if route_preference in switcher:
        recommendation = switcher[route_preference]['recommendation']
        alternatives = switcher[route_preference]['alternatives']
    else:
        recommendation = 'Based on general traffic patterns, here are the recommended departure times.'
        alternatives = [
            {'time': '8:00 AM', 'description': 'Morning departure - good balance of visibility and traffic', 'rating': 'optimal'},
            {'time': '2:00 PM', 'description': 'Afternoon departure - moderate traffic conditions', 'rating': 'good'},
            {'time': '6:00 PM', 'description': 'Evening departure - rush hour traffic expected', 'rating': 'avoid'}
        ]
    
    return {
        'recommendation': recommendation,
        'alternatives': alternatives,
        'preferred_date': preferred_date,
        'preferred_time': preferred_time,
        'route_preference': route_preference
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)  # Disable reloader to avoid watchdog issues
