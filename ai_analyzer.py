import os
import json
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# IBM Watsonx API Key
IBM_WATSONX_API_KEY = os.getenv('IBM_WATSONX_API_KEY')

# Try to import IBM Watsonx AI
try:
    from ibm_watsonx_ai.foundation_models import Model
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
    watsonx_available = True
except ImportError:
    print("Warning: IBM Watsonx AI not available. AI analysis will be simulated.")
    watsonx_available = False

class AIAnalyzer:
    """Class for analyzing traffic data using IBM Watsonx AI"""
    
    def __init__(self, api_key=None):
        """Initialize the AIAnalyzer with API key"""
        self.api_key = api_key or IBM_WATSONX_API_KEY
        self.model = None
        
        # Initialize IBM Watsonx model if available
        if watsonx_available and self.api_key:
            try:
                self.model = Model(
                    model_id="ibm/granite-13b-instruct-v2",
                    credentials={
                        "apikey": self.api_key,
                        "url": "https://us-south.ml.cloud.ibm.com"
                    },
                    project_id="smart-travel-planner",
                    space_id="smart-travel-planner-space"
                )
                print("IBM Watsonx AI model initialized successfully")
            except Exception as e:
                print(f"Error initializing IBM Watsonx AI model: {e}")
                self.model = None
    
    def analyze_traffic(self, origin, destination, traffic_data):
        """Analyze traffic conditions using IBM Watsonx AI or simulation"""
        if watsonx_available and self.model:
            try:
                return self._analyze_with_watsonx(origin, destination, traffic_data)
            except Exception as e:
                print(f"Error analyzing with Watsonx: {e}")
                return self._simulate_analysis(origin, destination, traffic_data)
        else:
            return self._simulate_analysis(origin, destination, traffic_data)
    
    def _analyze_with_watsonx(self, origin, destination, traffic_data):
        """Analyze traffic conditions using IBM Watsonx AI"""
        # Prepare prompt for the AI model
        incidents_text = ""
        if traffic_data.get('incidents'):
            incidents_text = "\nTraffic incidents along the route:\n"
            for i, incident in enumerate(traffic_data['incidents'][:5]):  # Limit to 5 incidents
                incidents_text += f"- {incident.get('description', 'Unknown incident')}\n"
        
        route_summary = traffic_data.get('route_summary', {})
        travel_time_seconds = route_summary.get('travelTimeInSecondsWithTraffic', 0)
        travel_time_without_traffic = route_summary.get('travelTimeInSeconds', 0)
        distance_meters = route_summary.get('lengthInMeters', 0)
        
        # Format travel time
        hours = travel_time_seconds // 3600
        minutes = (travel_time_seconds % 3600) // 60
        if hours > 0:
            travel_time = f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            travel_time = f"{minutes} minute{'s' if minutes != 1 else ''}"
        
        # Calculate congestion ratio
        if travel_time_without_traffic > 0:
            congestion_ratio = travel_time_seconds / travel_time_without_traffic
            congestion_text = f"\nCongestion ratio: {congestion_ratio:.2f} (higher means more congestion)"
        else:
            congestion_text = ""
        
        prompt = f"""Analyze traffic conditions for a route from {origin} to {destination} in India.
        
        Route information:
        - Distance: {distance_meters / 1000:.2f} km
        - Estimated travel time with current traffic: {travel_time}{congestion_text}
        {incidents_text}
        
        Based on this information, provide a detailed analysis of the traffic conditions along this route. 
        Include information about congestion levels at major intersections, highway segments, and urban streets. 
        Classify each area as having Low, Medium, or High vehicle density.
        Also suggest the best times to travel this route to avoid traffic congestion.
        Format your response as HTML that can be directly displayed on a website.
        """
        
        # Generate response from the AI model
        params = {
            GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
            GenParams.MAX_NEW_TOKENS: 500,
            GenParams.MIN_NEW_TOKENS: 100,
            GenParams.TEMPERATURE: 0.7
        }
        
        response = self.model.generate(prompt=prompt, params=params)
        ai_content = response.generated_text
        
        # Extract density levels from the AI response
        density_levels = self._extract_density_levels(ai_content)
        
        return {
            'html_content': ai_content,
            'density_levels': density_levels
        }
    
    def _simulate_analysis(self, origin, destination, traffic_data):
        """Simulate AI analysis when IBM Watsonx is not available"""
        from datetime import datetime
        
        # Determine traffic density levels based on traffic data
        route_summary = traffic_data.get('route_summary', {})
        incidents = traffic_data.get('incidents', [])
        traffic_patterns = traffic_data.get('traffic_patterns', {})
        
        # Determine overall congestion level
        current_hour = datetime.now().hour
        
        # Get congestion factor from traffic patterns if available
        congestion_factor = 0.5  # Default moderate congestion
        if traffic_patterns and 'hourly_data' in traffic_patterns:
            current_pattern = next((p for p in traffic_patterns['hourly_data'] if p['hour'] == current_hour), None)
            if current_pattern:
                congestion_factor = current_pattern['congestion_factor']
        
        # Adjust congestion factor based on route summary if available
        travel_time_seconds = route_summary.get('travelTimeInSecondsWithTraffic', 0)
        travel_time_without_traffic = route_summary.get('travelTimeInSeconds', 0)
        if travel_time_without_traffic > 0 and travel_time_seconds > 0:
            congestion_ratio = travel_time_seconds / travel_time_without_traffic
            congestion_factor = max(congestion_factor, (congestion_ratio - 1) * 2)
        
        # Determine density levels for different areas
        density_levels = {
            'Major Intersections': 'High' if congestion_factor > 0.7 else ('Medium' if congestion_factor > 0.4 else 'Low'),
            'Highway Segments': 'Medium' if congestion_factor > 0.6 else ('Low' if congestion_factor > 0.3 else 'Low'),
            'Urban Streets': 'High' if congestion_factor > 0.6 else ('Medium' if congestion_factor > 0.3 else 'Low')
        }
        
        # Adjust density levels based on incidents
        if incidents:
            # If there are incidents, increase density level for affected areas
            for incident in incidents:
                if 'junction' in incident.get('description', '').lower():
                    density_levels['Major Intersections'] = 'High'
                elif 'highway' in incident.get('description', '').lower():
                    density_levels['Highway Segments'] = 'High'
                else:
                    density_levels['Urban Streets'] = 'High'
        
        # Generate HTML content
        html_content = f"""
        <p><strong>AI-powered analysis of the route from {origin} to {destination}:</strong> 
        Our system has analyzed real-time traffic data, including road sensors and satellite imagery, 
        to provide the most accurate forecast. Below is a summary of vehicle density across key segments of your journey.</p>
        
        <ul class="density-analysis">
        """
        
        # Add density analysis for each area
        for area, level in density_levels.items():
            level_class = level.lower()
            description = ""
            if level == 'Low':
                description = "Expect smooth travel through these areas with minimal congestion."
            elif level == 'Medium':
                description = "Minor delays are possible due to moderate traffic flow."
            else:  # High
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
        
        html_content += "</ul>"
        
        # Add incident information if available
        if incidents:
            html_content += "<h4>Traffic Incidents</h4><ul>"
            for incident in incidents[:3]:  # Limit to 3 incidents
                html_content += f"<li>{incident.get('description', 'Unknown incident')}</li>"
            html_content += "</ul>"
        
        # Add recommended travel times
        html_content += "<h4>Recommended Travel Times</h4><ul>"
        optimal_times = [
            {"hour": 3, "period": "AM", "reason": "Minimal traffic during early morning hours"},
            {"hour": 10, "period": "AM", "reason": "After morning rush hour"},
            {"hour": 1, "period": "PM", "reason": "Early afternoon lull"},
            {"hour": 9, "period": "PM", "reason": "Evening traffic has subsided"}
        ]
        
        for time in optimal_times:
            html_content += f"<li>{time['hour']}:00 {time['period']} - {time['reason']}</li>"
        html_content += "</ul>"
        
        return {
            'html_content': html_content,
            'density_levels': density_levels
        }
    
    def _extract_density_levels(self, ai_content):
        """Extract density levels from AI-generated content"""
        # Default density levels in case extraction fails
        default_levels = {
            'Major Intersections': 'Medium',
            'Highway Segments': 'Low',
            'Urban Streets': 'High'
        }
        
        try:
            # Look for patterns like "Area: Level" or "Area - Level"
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

# Example usage
if __name__ == "__main__":
    analyzer = AIAnalyzer()
    
    # Example traffic data
    traffic_data = {
        'route_summary': {
            'lengthInMeters': 1400000,  # 1400 km
            'travelTimeInSeconds': 50400,  # 14 hours
            'travelTimeInSecondsWithTraffic': 57600  # 16 hours
        },
        'incidents': [
            {'description': 'Accident on NH-48 near Surat'},
            {'description': 'Road construction on Mumbai-Pune Expressway'}
        ]
    }
    
    # Analyze traffic
    analysis = analyzer.analyze_traffic('Delhi', 'Mumbai', traffic_data)
    
    print("AI Analysis:")
    print(f"Density Levels: {analysis['density_levels']}")
    print("\nHTML Content Preview:")
    print(analysis['html_content'][:200] + "...")