# AI-Powered Smart Travel Planner

A web application that helps users find the best route and optimal departure time for their trips in India, powered by AI analysis of traffic patterns.

> **[UPDATED]** The AI analysis module has been fully implemented with IBM Watsonx integration for advanced traffic pattern analysis.

## Why This Matters

Urban traffic congestion is not just an inconvenience — it’s a **major economic, environmental, and social challenge**:

- **Economic impact**: In India, commuters lose millions of productive hours each day stuck in traffic, translating into billions of rupees in lost productivity annually.
- **Environmental costs**: Idling vehicles release significant amounts of greenhouse gases and harmful pollutants, worsening air quality and contributing to climate change.
- **Social consequences**: Long, stressful commutes reduce quality of life, increase stress levels, and leave less time for family, rest, and well-being.

Our solution leverages the power of **IBM watsonx™ AI** to go beyond traditional maps and estimated travel times. It provides **deeper insights and smarter alternatives** by:

- Suggesting the **optimal departure time** to minimize travel delays
- Recommending **eco-friendly routes** to reduce carbon emissions
- Offering **low-traffic routes** for a smoother, stress-free driving experience
- Highlighting **scenic routes** that turn a commute into an enjoyable journey

The outcome is a **smarter, more sustainable travel experience** that balances efficiency, personal comfort, and environmental responsibility.

## Features

- User-friendly interface for entering origin and destination locations
- Interactive map display for visualizing routes
- AI-powered analysis of vehicle density at intersections and streets
- Optimal departure time recommendations based on traffic patterns
- Estimated travel time calculations

## Technologies

### Frontend
- HTML5
- CSS3 (with animations and responsive design)
- JavaScript (vanilla JS for DOM manipulation and event handling)
- Leaflet.js for interactive maps

### Backend
- Python 3.x
- Flask web framework
- Flask-CORS for cross-origin resource sharing
- Pandas and NumPy for data processing
- Geopy for geocoding and distance calculations
- Requests for API communication

## Project Structure

```
├── css/
│   └── style.css                # Styling for the application
├── js/
│   └── app.js                   # Frontend JavaScript functionality
├── docs/                        # Documentation files
│   ├── AI_ANALYSIS_SOURCE_TRACKING.md
│   ├── IBM_GRANITE_MODEL.md
│   ├── IBM_WX_LLMS_EXAMPLES.md
│   ├── LEAFLET_IMPLEMENTATION.md
│   └── OPENSTREETMAP_CORS_FIX.md
├── app.py                       # Flask backend server
├── ai_analyzer.py               # AI analysis module with IBM Watsonx integration
├── traffic_analyzer.py          # Traffic data analysis module
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment variables
└── index.html                   # Main HTML structure
```

## Getting Started

1. Clone the repository
2. Create a `.env` file based on `.env.example` and add your API keys:
   - TomTom API key for traffic data
   - IBM Watsonx API key for AI-powered traffic analysis
3. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Start the Flask backend server:
   ```
   python app.py
   ```
5. Open `index.html` in your browser or access the application at `http://localhost:5000`
6. Enter your origin and destination locations
7. Click "Plan My Trip" to see the results

## Recent Enhancements

### Route Preference System
> **[NEW]** Added comprehensive route preference system with four distinct route types and AI-powered recommendations.

The application now supports **four specialized route preferences** to cater to different user needs:

- **Fastest Route**: Prioritizes minimal travel time regardless of traffic conditions
- **Eco-Friendly Route**: Minimizes carbon emissions and environmental impact
- **Low-Traffic Route**: Avoids congested areas for a smoother driving experience
- **Scenic Route**: Features routes with higher scenic ratings and enjoyable views

### Enhanced AI Analysis
> **[NEW]** AI analysis now incorporates route preferences for personalized travel recommendations.

Key improvements include:
- **Route-specific AI prompts** that consider the selected preference type
- **Dynamic traffic density mapping** adjusted based on route preference
- **Personalized departure time recommendations** tailored to each route type
- **Enhanced Watsonx integration** with preference-aware analysis
- **Fallback simulation analysis** that maintains preference logic even when API calls fail

### API Enhancements
> **[NEW]** Updated `/plan_trip` endpoint with new parameters and improved AI integration.

The backend API now accepts:
- `preferred_date`: Specific date for trip planning (YYYY-MM-DD format)
- `preferred_time`: Preferred departure time window (morning/afternoon/evening/night)
- `route_preference`: Selected route type (fastest/eco-friendly/low-traffic/scenic)

### Technical Improvements
- **TrafficAnalyzer.py**: Enhanced with `get_routes_by_preference` method for preference-based route filtering
- **AIAnalyzer.py**: Updated methods to accept and process route preference parameters
- **App.py**: Comprehensive updates to all major functions including `plan_trip`, `generate_optimal_timing`, `generate_ai_analysis`, and `simulate_ai_analysis`

## Current Status

- ✅ Frontend implementation complete
- ✅ Backend server with Flask implemented
- ✅ Traffic analysis module using TomTom API implemented
- ✅ AI analysis module fully implemented with IBM Watsonx integration
- ✅ Route preference system with 4 route types
- ✅ Dynamic route selection based on user preferences
- ✅ Enhanced AI analysis with personalized recommendations
- ✅ TomTom API integration for traffic-aware preferences

## Future Enhancements

- User authentication and saved trips
- Mobile application version
- Integration with real-time weather data
- Offline mode support
- Enhanced AI predictions with historical traffic data

## License

MIT
