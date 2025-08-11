# AI-Powered Smart Travel Planner

A web application that helps users find the best route and optimal departure time for their trips in India, powered by AI analysis of traffic patterns.

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
├── ai_analyzer.py               # AI analysis module (to be implemented)
├── traffic_analyzer.py          # Traffic data analysis module
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment variables
└── index.html                   # Main HTML structure
```

## Getting Started

1. Clone the repository
2. Create a `.env` file based on `.env.example` and add your API keys:
   - TomTom API key for traffic data
   - IBM Watsonx API key (will be used in future updates)
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

## Current Status

- ✅ Frontend implementation complete
- ✅ Backend server with Flask implemented
- ✅ Traffic analysis module using TomTom API implemented
- ⏳ AI analysis module structure created (to be fully implemented soon)

## Future Enhancements

- Complete IBM Watsonx AI integration for advanced traffic pattern analysis
- User authentication and saved trips
- Mobile application version
- Integration with real-time weather data
- Offline mode support

## License

MIT