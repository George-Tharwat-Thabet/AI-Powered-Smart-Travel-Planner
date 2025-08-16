// Smart Travel Planner JavaScript

// Global variables for map markers and route lines
let originMarker = null;
let destinationMarker = null;
let routeLine = null;
let routeOutline = null;

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const planTripBtn = document.getElementById('plan-trip-btn');
    const originInput = document.getElementById('origin');
    const destinationInput = document.getElementById('destination');
    // MODIFIED: Added new variables for the new form elements (line 12-14)
    const preferredDateInput = document.getElementById('preferred-date');
    const preferredTimeInput = document.getElementById('preferred-time');
    const routePreferenceSelect = document.getElementById('route-preference');
    
    const resultsSection = document.getElementById('results');
    const bestRouteElement = document.getElementById('best-route');
    const departureTimeElement = document.getElementById('departure-time');
    const travelTimeElement = document.getElementById('travel-time');
    const aiAnalysisElement = document.getElementById('ai-analysis');
    // ADDED: Get new result elements (line 24-26)
    const optimalTimingElement = document.getElementById('optimal-timing');
    const timingAlternativesElement = document.getElementById('timing-alternatives');
    
    // Initialize autocomplete for Indian locations
    initializeAutocomplete(originInput);
    initializeAutocomplete(destinationInput);
    
    // Initialize the map when the page loads
    // Global variable to track if map is already initialized
    window.mapInitialized = false;
    updateMap();
    
    // Add event listener to the Plan My Trip button
    planTripBtn.addEventListener('click', handlePlanTrip);
    
    /**
     * Function to handle the trip planning process
     * This function will be called when the "Plan My Trip" button is clicked
     */
    function handlePlanTrip() {
        // Get values from input fields
        const origin = originInput.value.trim();
        const destination = destinationInput.value.trim();
        const preferredDate = preferredDateInput.value; // ADDED
        const preferredTime = preferredTimeInput.value; // ADDED
        const routePreference = routePreferenceSelect.value; // ADDED
        
        // Validate inputs
        if (!origin || !destination) {
            alert('Please enter both origin and destination');
            return;
        }
        
        // If map is already initialized with markers from clicking, use those instead of reinitializing
        if (window.mapInitialized && window.leafletMap) {
            // We already have markers set by clicking on the map or from previous searches
            console.log('Using existing map');
            
            // If we don't have markers yet, we'll need to geocode the addresses and set markers
            if (!originMarker || !destinationMarker) {
                // This will be handled by the backend response
                console.log('Need to set markers from addresses');
            }
        }
        
        // Log the values to the console (for development purposes)
        console.log('Origin:', origin);
        console.log('Destination:', destination);
        
        // Make API call to the Python backend to get route details
        planTripBtn.innerHTML = '<span class="loading-text">Processing...</span>';
        planTripBtn.disabled = true;
        planTripBtn.classList.add('loading');
        
        fetch('http://localhost:5000/api/plan-trip', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                origin: origin,
                destination: destination,
                preferred_date: preferredDate, // ADDED
                preferred_time: preferredTime, // ADDED
                route_preference: routePreference // ADDED
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update the UI with the results
            updateResults(data);
            // Update the map with the route
            if (data.routePoints) {
                updateMap(data.routePoints);
            }
            
            // Reset button
            planTripBtn.innerHTML = 'Plan My Trip';
            planTripBtn.disabled = false;
            planTripBtn.classList.remove('loading');
            
            // Show the results section
            resultsSection.style.display = 'block';
            resultsSection.classList.add('visible');
            
            // Scroll to the results section
            resultsSection.scrollIntoView({ behavior: 'smooth' });
            
            // Add animation to result cards
            const resultCards = document.querySelectorAll('.result-card');
            resultCards.forEach((card, index) => {
                card.style.setProperty('--card-index', index);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while planning your trip. Please try again.');
            
            // Reset button
            planTripBtn.innerHTML = 'Plan My Trip';
            planTripBtn.disabled = false;
            planTripBtn.classList.remove('loading');
            
            // Fall back to simulation for demo purposes
            simulateApiResponse(origin, destination);
        });
    }
    
    /**
     * Function to simulate an API response (for development purposes)
     * @param {string} origin - The origin location
     * @param {string} destination - The destination location
     */
    // MODIFIED: Updated simulateApiResponse to include new timing analysis (line 300-320) 
    function simulateApiResponse(origin, destination) { 
        // Add loading animation to button 
        planTripBtn.innerHTML = '<span class="loading-text">Processing...</span>'; 
        planTripBtn.disabled = true; 
        planTripBtn.classList.add('loading'); 
        
        // Simulate loading time 
        setTimeout(() => { 
            const routePreference = routePreferenceSelect.value; // ADDED 
            
            // MODIFIED: Updated mock data to include route preference info 
            const mockData = { 
                bestRoute: `${origin} → ${getRouteDescription(routePreference)} → ${destination}`, 
                departureTime: preferredTimeInput.value || '08:30 AM', // MODIFIED 
                travelTime: calculateTravelTime(routePreference), // MODIFIED 
                aiAnalysis: generateAIAnalysis(origin, destination), 
                routePreference: routePreference // ADDED 
            }; 
            
            // Update the UI with the mock results 
            updateResults(mockData); 
            
            // Reset button 
            planTripBtn.innerHTML = 'Plan My Trip'; 
            planTripBtn.disabled = false; 
            planTripBtn.classList.remove('loading'); 
            
            // Show the results section 
            resultsSection.style.display = 'block'; 
            resultsSection.classList.add('visible'); 
            
            // Scroll to the results section 
            resultsSection.scrollIntoView({ behavior: 'smooth' }); 
            
            // Add animation to result cards 
            const resultCards = document.querySelectorAll('.result-card'); 
            resultCards.forEach((card, index) => { 
                card.style.setProperty('--card-index', index); 
            }); 
        }, 2000); // Simulate 2 seconds of loading time 
    } 
    
    // ADDED: Helper function to get route description based on preference (line 340-355) 
    function getRouteDescription(routePreference) { 
        switch (routePreference) { 
            case 'fastest': 
                return 'Express Highway (Fastest Route)'; 
            case 'eco-friendly': 
                return 'Green Route (Low Emissions)'; 
            case 'low-traffic': 
                return 'Alternative Roads (Traffic-Free)'; 
            case 'scenic': 
                return 'Scenic Highway (Beautiful Views)'; 
            default: 
                return 'NH-48'; 
        } 
    } 
    
    // ADDED: Helper function to calculate travel time based on route preference (line 357-375) 
    function calculateTravelTime(routePreference) { 
        const baseTravelTime = 135; // Base time in minutes (2 hours 15 minutes) 
        let modifier = 1; 
        
        switch (routePreference) { 
            case 'fastest': 
                modifier = 0.85; // 15% faster 
                break; 
            case 'eco-friendly': 
                modifier = 1.1; // 10% slower but eco-friendly 
                break; 
            case 'low-traffic': 
                modifier = 0.95; // 5% faster due to no traffic 
                break; 
            case 'scenic': 
                modifier = 1.3; // 30% slower but scenic 
                break; 
        } 
        
        const totalMinutes = Math.round(baseTravelTime * modifier); 
        const hours = Math.floor(totalMinutes / 60); 
        const minutes = totalMinutes % 60; 
        
        return `${hours} hour${hours !== 1 ? 's' : ''} ${minutes} minute${minutes !== 1 ? 's' : ''}`; 
    }
    
    /**
     * Function to update the UI with the results
     * @param {Object} data - The data containing the route details
     */
    function updateResults(data) {
        bestRouteElement.textContent = data.bestRoute;
        departureTimeElement.textContent = data.departureTime;
        travelTimeElement.textContent = data.travelTime;
        
        // ADDED: Update optimal timing section
        if (data.optimalTiming) {
            optimalTimingElement.textContent = data.optimalTiming.recommendation || 'AI analysis will provide optimal timing suggestions based on your preferences.';
            
            // ADDED: Populate timing alternatives
            if (data.optimalTiming.alternatives && data.optimalTiming.alternatives.length > 0) {
                let timingHTML = '';
                data.optimalTiming.alternatives.forEach((timing, index) => {
                    const badgeClass = timing.rating === 'optimal' ? 'optimal' : 
                                     timing.rating === 'good' ? 'good' : 'avoid';
                    
                    timingHTML += `
                        <div class="timing-option ${timing.rating === 'optimal' ? 'recommended' : ''}" style="--timing-index: ${index}">
                            <div class="timing-info">
                                <div class="timing-time">${timing.time}</div>
                                <div class="timing-description">${timing.description}</div>
                            </div>
                            <span class="timing-badge ${badgeClass}">${timing.rating}</span>
                        </div>
                    `;
                });
                timingAlternativesElement.innerHTML = timingHTML;
            }
        } else {
            // ADDED: Fallback for when no optimal timing data is available
            generateOptimalTimingAnalysis(data);
        }
        
        // Add AI source information to the analysis
        let aiContent = data.aiAnalysis;
        
        // Check if aiAnalysis is HTML content or plain text
        if (aiContent && !aiContent.startsWith('<')) {
            // If it's plain text, wrap it in paragraph tags
            aiContent = `<p>${aiContent}</p>`;
        }
        
        // Add AI source information at the end of the analysis
        if (data.aiSource) {
            const aiSourceInfo = `
            <div class="ai-source-info">
                <p class="ai-source-text">
                    <small>
                        <strong>AI Source:</strong> ${data.aiSource === 'ibm_watsonx' ? 'IBM Watsonx AI' : 'Simulation'}
                        ${data.aiModel ? ` | <strong>Model:</strong> ${data.aiModel}` : ''}
                        ${data.aiTimestamp ? ` | Generated at: ${new Date(data.aiTimestamp).toLocaleTimeString()}` : ''}
                    </small>
                </p>
            </div>`;
            
            aiContent += aiSourceInfo;
        }
        
        aiAnalysisElement.innerHTML = aiContent;
        
        // Ensure density indicators are properly displayed
        const densityLevels = document.querySelectorAll('.density-level span');
        if (densityLevels.length > 0) {
            densityLevels.forEach(span => {
                span.classList.add('pulse');
            });
        }
    }
    
    /**
     * Function to generate optimal timing analysis when no backend data is available
     * @param {Object} data - The route data from the backend
     */
    function generateOptimalTimingAnalysis(data) {
        const routePreference = routePreferenceSelect.value;
        const currentHour = new Date().getHours();
        
        // Generate timing recommendations based on route preference
        let timingRecommendation = '';
        let alternatives = [];
        
        switch (routePreference) {
            case 'fastest':
                timingRecommendation = 'For the fastest route, avoid peak hours (7-10 AM and 5-8 PM) when traffic is heaviest.';
                alternatives = [
                    { time: '6:00 AM', description: 'Early morning departure - minimal traffic, fastest travel time', rating: 'optimal' },
                    { time: '10:30 AM', description: 'Mid-morning - light traffic, good travel conditions', rating: 'good' },
                    { time: '2:00 PM', description: 'Early afternoon - moderate traffic, decent travel time', rating: 'good' },
                    { time: '8:00 AM', description: 'Peak morning rush - heavy traffic, longer travel time', rating: 'avoid' }
                ];
                break;
                
            case 'eco-friendly':
                timingRecommendation = 'For an eco-friendly route with lower emissions, travel during off-peak hours when engines run more efficiently.';
                alternatives = [
                    { time: '9:30 AM', description: 'Post rush hour - steady traffic flow, better fuel efficiency', rating: 'optimal' },
                    { time: '2:30 PM', description: 'Afternoon travel - consistent speeds, lower emissions', rating: 'optimal' },
                    { time: '11:00 PM', description: 'Late night - free-flowing traffic, minimal stops', rating: 'good' },
                    { time: '7:30 AM', description: 'Rush hour - stop-and-go traffic increases emissions', rating: 'avoid' }
                ];
                break;
                
            case 'low-traffic':
                timingRecommendation = 'To avoid traffic congestion, plan your departure outside of peak commuting hours.';
                alternatives = [
                    { time: '5:30 AM', description: 'Very early departure - roads are clear, no congestion', rating: 'optimal' },
                    { time: '11:00 AM', description: 'Late morning - traffic has cleared, smooth journey', rating: 'optimal' },
                    { time: '9:00 PM', description: 'Evening departure - rush hour has ended', rating: 'good' },
                    { time: '6:00 PM', description: 'Evening rush hour - expect heavy congestion', rating: 'avoid' }
                ];
                break;
                
            case 'scenic':
                timingRecommendation = 'For a scenic route, travel during daylight hours to enjoy the views. Golden hours provide the best lighting.';
                alternatives = [
                    { time: '7:00 AM', description: 'Golden hour departure - beautiful sunrise views along the route', rating: 'optimal' },
                    { time: '4:00 PM', description: 'Afternoon departure - good lighting for scenic photography', rating: 'optimal' },
                    { time: '11:00 AM', description: 'Mid-morning - clear visibility, pleasant weather', rating: 'good' },
                    { time: '9:00 PM', description: 'Night travel - limited scenic visibility', rating: 'avoid' }
                ];
                break;
                
            default:
                timingRecommendation = 'Based on general traffic patterns, here are the recommended departure times.';
                alternatives = [
                    { time: '8:00 AM', description: 'Morning departure - good balance of visibility and traffic', rating: 'optimal' },
                    { time: '2:00 PM', description: 'Afternoon departure - moderate traffic conditions', rating: 'good' },
                    { time: '6:00 PM', description: 'Evening departure - rush hour traffic expected', rating: 'avoid' }
                ];
        }
        
        // Update the optimal timing section
        optimalTimingElement.textContent = timingRecommendation;
        
        // Populate timing alternatives
        let timingHTML = '';
        alternatives.forEach((timing, index) => {
            const badgeClass = timing.rating === 'optimal' ? 'optimal' : 
                             timing.rating === 'good' ? 'good' : 'avoid';
            
            timingHTML += `
                <div class="timing-option ${timing.rating === 'optimal' ? 'recommended' : ''}" style="--timing-index: ${index}">
                    <div class="timing-info">
                        <div class="timing-time">${timing.time}</div>
                        <div class="timing-description">${timing.description}</div>
                    </div>
                    <span class="timing-badge ${badgeClass}">${timing.rating}</span>
                </div>
            `;
        });
        timingAlternativesElement.innerHTML = timingHTML;
    }
    
    /**
     * Function to generate AI analysis of vehicle density
     * @param {string} origin - The origin location
     * @param {string} destination - The destination location
     * @returns {string} - HTML content for the analysis
     */
    function generateAIAnalysis(origin, destination) {
        // This would be replaced with actual AI analysis from the backend
        // For now, we'll generate some mock analysis
        
        // Randomly determine traffic density levels for different areas
        const areas = [
            { name: 'Major Intersections', level: getRandomDensityLevel() },
            { name: 'Highway Segments', level: getRandomDensityLevel() },
            { name: 'Urban Streets', level: getRandomDensityLevel() }
        ];
        
        // Create HTML for the analysis
        let analysisHTML = `<p><strong>AI-powered analysis of the route from ${origin} to ${destination}:</strong> Our system has analyzed real-time traffic data, including road sensors and satellite imagery, to provide the most accurate forecast. Below is a summary of vehicle density across key segments of your journey.</p>`;
        analysisHTML += '<ul class="density-analysis">';
        
        areas.forEach(area => {
            const levelClass = area.level.toLowerCase();
            let description = '';
            switch (area.level) {
                case 'Low':
                    description = 'Expect smooth travel through these areas with minimal congestion.';
                    break;
                case 'Medium':
                    description = 'Minor delays are possible due to moderate traffic flow.';
                    break;
                case 'High':
                    description = 'Significant delays are likely; consider alternative routes if possible.';
                    break;
            }
            analysisHTML += `<li><div class="analysis-item"><span class="area-name">${area.name}</span><p class="area-description">${description}</p></div><span class="density-value ${levelClass}">${area.level}</span></li>`;
        });
        
        analysisHTML += '</ul>';
        return analysisHTML;
    }
    
    /**
     * Helper function to get a random density level
     * @returns {string} - Random density level (Low, Medium, or High)
     */
    function getRandomDensityLevel() {
        const levels = ['Low', 'Medium', 'High'];
        const randomIndex = Math.floor(Math.random() * levels.length);
        return levels[randomIndex];
    }
    
    /**
     * Helper function to get a random traffic color
     * @returns {string} - Random traffic color (hex code)
     */
    function getRandomTrafficColor() {
        const trafficColors = [
            '#4CAF50', // Green - free flow
            '#FFC107', // Amber - slow
            '#FF9800', // Orange - queuing
            '#F44336'  // Red - stationary
        ];
        const randomIndex = Math.floor(Math.random() * trafficColors.length);
        return trafficColors[randomIndex];
    }
    
    /**
     * Function to update the map with the route
     * @param {Array} routePoints - The route coordinates (optional)
     */
    function updateMap(routePoints) {
        // Get the map container element
        const mapContainer = document.getElementById('map');
        
        // Check if we have a map already
        if (window.mapInitialized && window.leafletMap) {
            // If we have route points, update the map with them
            if (routePoints && routePoints.length > 0) {
                // Clear existing route lines if they exist
                if (routeLine) window.leafletMap.removeLayer(routeLine);
                if (routeOutline) window.leafletMap.removeLayer(routeOutline);
                
                // Update markers and route based on new route points
                const firstPoint = routePoints[0];
                const lastPoint = routePoints[routePoints.length - 1];
                
                // Update or create markers
                updateOrCreateMarkers(firstPoint, lastPoint);
                
                // Draw route line between points
                drawRouteFromPoints(routePoints);
                
                // Fit map to show the entire route
                const bounds = L.latLngBounds(routePoints.map(point => [point.lat, point.lon]));
                window.leafletMap.fitBounds(bounds, { padding: [50, 50] });
                
                return;
            }
            return; // Keep existing map if no route points
        }
        
        // If we reach here, we need to initialize the map
        if (!routePoints || routePoints.length === 0) {
            // Initialize empty map that allows user selection
            initializeMap();
            return;
        }
        
        // Initialize the map with Leaflet and route points
        initializeMap(routePoints);
    }
    
    /**
     * Helper function to update or create markers based on route points
     * @param {Object} firstPoint - The first point in the route
     * @param {Object} lastPoint - The last point in the route
     */
    function updateOrCreateMarkers(firstPoint, lastPoint) {
        // Remove existing markers if they exist
        if (originMarker) window.leafletMap.removeLayer(originMarker);
        if (destinationMarker) window.leafletMap.removeLayer(destinationMarker);
        
        // Create origin marker
        const originIcon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
        
        // Create destination marker
        const destinationIcon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
        
        // Set origin marker
        originMarker = L.marker([firstPoint.lat, firstPoint.lon], {icon: originIcon})
            .addTo(window.leafletMap)
            .bindPopup("Origin: " + (firstPoint.name || 'Selected location'))
            .openPopup();
        
        // Set destination marker
        destinationMarker = L.marker([lastPoint.lat, lastPoint.lon], {icon: destinationIcon})
            .addTo(window.leafletMap)
            .bindPopup("Destination: " + (lastPoint.name || 'Selected location'))
            .openPopup();
    }
    
    /**
     * Helper function to draw route line from route points
     * @param {Array} routePoints - The route coordinates
     */
    function drawRouteFromPoints(routePoints) {
        // Convert route points to LatLng objects
        const routeCoordinates = routePoints.map(point => [point.lat, point.lon]);
        
        // Create route outline (thicker, black line underneath for visual effect)
        routeOutline = L.polyline(routeCoordinates, {
            color: 'black',
            weight: 8,
            opacity: 0.5
        }).addTo(window.leafletMap);
        
        // Create route line with traffic-based coloring
        routeLine = L.polyline(routeCoordinates, {
            color: getRandomTrafficColor(),
            weight: 5,
            opacity: 0.8,
            dashArray: '10, 10',
            lineCap: 'round'
        }).addTo(window.leafletMap);
    }
    
    /**
     * Initialize the map with Leaflet
     * @param {Array} routePoints - The route coordinates (optional)
     */
    function initializeMap(routePoints = null) {
        // Set default center of India if no route points
        let mapCenter = [20.5937, 78.9629]; // Center of India
        let zoomLevel = 5;
        
        // If route points are provided, use them
        if (routePoints && routePoints.length > 0) {
            const firstPoint = routePoints[0];
            mapCenter = [firstPoint.lat, firstPoint.lon];
            zoomLevel = 10;
        }
        
        // Check if map is already initialized
        if (window.mapInitialized && window.leafletMap) {
            console.log('Map already initialized, updating view');
            window.leafletMap.setView(mapCenter, zoomLevel);
            return window.leafletMap;
        }
        
        // Initialize the map with Leaflet
        console.log('Initializing new map');
        window.leafletMap = L.map('map').setView(mapCenter, zoomLevel);
        window.mapInitialized = true;
        
        // Store map reference for later use
        const map = window.leafletMap;
        
        // Add OpenStreetMap tile layer with CORS-friendly provider
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            subdomains: ['a', 'b', 'c'],
            crossOrigin: true,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
        
        // Create custom icons for origin and destination
        const originIcon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
        
        const destinationIcon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
        
        // Use global selection mode variable
        let selectionMode = 'origin'; // Default selection mode
        
        // Add click event to show coordinates and set markers
        const coordInfo = L.control({position: 'bottomleft'});
        coordInfo.onAdd = function() {
            const div = L.DomUtil.create('div', 'coordinate-info');
            div.innerHTML = 'Click on map to set origin and destination points';
            div.style.backgroundColor = 'white';
            div.style.padding = '5px';
            div.style.borderRadius = '5px';
            div.style.boxShadow = '0 1px 5px rgba(0,0,0,0.4)';
            return div;
        };
        coordInfo.addTo(map);
        
        // Add selection mode toggle control
        const selectionControl = L.control({position: 'topright'});
        selectionControl.onAdd = function() {
            const div = L.DomUtil.create('div', 'selection-control');
            div.innerHTML = `
                <div class="selection-toggle">
                    <div class="toggle-label">Selection Mode:</div>
                    <div class="toggle-buttons">
                        <button class="toggle-btn active" data-mode="origin">Origin</button>
                        <button class="toggle-btn" data-mode="destination">Destination</button>
                    </div>
                </div>
            `;
            div.style.backgroundColor = 'white';
            div.style.padding = '10px';
            div.style.borderRadius = '5px';
            div.style.boxShadow = '0 1px 5px rgba(0,0,0,0.4)';
            
            // Add event listeners to toggle buttons
            setTimeout(() => {
                const buttons = div.querySelectorAll('.toggle-btn');
                buttons.forEach(button => {
                    button.addEventListener('click', function() {
                        // Remove active class from all buttons
                        buttons.forEach(btn => btn.classList.remove('active'));
                        // Add active class to clicked button
                        this.classList.add('active');
                        // Set selection mode
                        selectionMode = this.getAttribute('data-mode');
                    });
                });
            }, 0);
            
            return div;
        };
        selectionControl.addTo(map);
        
        // Function to get address from coordinates using reverse geocoding
        async function getAddressFromCoordinates(lat, lng) {
            try {
                const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`);
                const data = await response.json();
                return data.display_name || 'Unknown location';
            } catch (error) {
                console.error('Error getting address:', error);
                return 'Unknown location';
            }
        }
        
        // Click event handler for the map
        map.on('click', async function(e) {
            const lat = e.latlng.lat;
            const lng = e.latlng.lng;
            
            // Update coordinate info
            coordInfo.getContainer().innerHTML = 
                `<b>Latitude:</b> ${lat.toFixed(5)}<br>
                 <b>Longitude:</b> ${lng.toFixed(5)}`;
            
            // Get address from coordinates
            const address = await getAddressFromCoordinates(lat, lng);
            
            if (selectionMode === 'origin') {
                // Remove existing origin marker if it exists
                if (originMarker) {
                    map.removeLayer(originMarker);
                }
                
                // Set origin marker
                originMarker = L.marker([lat, lng], {icon: originIcon})
                    .addTo(map)
                    .bindPopup("Origin: " + address)
                    .openPopup();
                
                // Update origin input field without triggering map reinitialization
                const originInput = document.getElementById('origin');
                originInput.value = address;
                
                // Draw route if both markers exist
                if (destinationMarker) {
                    // Remove existing route line
                    if (routeLine) map.removeLayer(routeLine);
                    if (routeOutline) map.removeLayer(routeOutline);
                    
                    // Draw new route line
                    drawRouteLine(originMarker.getLatLng(), destinationMarker.getLatLng());
                }
            } else if (selectionMode === 'destination') {
                // Remove existing destination marker if it exists
                if (destinationMarker) {
                    map.removeLayer(destinationMarker);
                }
                
                // Set destination marker
                destinationMarker = L.marker([lat, lng], {icon: destinationIcon})
                    .addTo(map)
                    .bindPopup("Destination: " + address)
                    .openPopup();
                
                // Update destination input field without triggering map reinitialization
                const destinationInput = document.getElementById('destination');
                destinationInput.value = address;
                
                // Draw route if both markers exist
                if (originMarker) {
                    // Remove existing route line
                    if (routeLine) map.removeLayer(routeLine);
                    if (routeOutline) map.removeLayer(routeOutline);
                    
                    // Draw new route line
                    drawRouteLine(originMarker.getLatLng(), destinationMarker.getLatLng());
                    
                    // Trigger trip planning with the selected coordinates
                    planTripWithCoordinates(originMarker.getLatLng(), destinationMarker.getLatLng());
                }
            }
        });
        
        // Function to draw route line between two points
        function drawRouteLine(originLatLng, destLatLng) {
            const routeCoordinates = [
                [originLatLng.lat, originLatLng.lng],
                [destLatLng.lat, destLatLng.lng]
            ];
            
            // Add route outline (shadow effect)
            routeOutline = L.polyline(routeCoordinates, {
                color: '#000',
                weight: 12,
                opacity: 0.4
            }).addTo(map);
            
            // Simulate traffic data
            // In a real implementation, you would fetch this from a traffic API
            const simulateTrafficData = () => {
                // Traffic flow levels: free-flow, slow, queuing, stationary
                const trafficLevels = ['free-flow', 'slow', 'queuing', 'stationary'];
                const randomIndex = Math.floor(Math.random() * trafficLevels.length);
                return trafficLevels[randomIndex];
            };
            
            // Get traffic color based on traffic level
            const getTrafficColor = (trafficLevel) => {
                switch(trafficLevel) {
                    case 'free-flow':
                        return '#4CAF50'; // Green
                    case 'slow':
                        return '#FFC107'; // Amber
                    case 'queuing':
                        return '#FF9800'; // Orange
                    case 'stationary':
                        return '#F44336'; // Red
                    default:
                        return '#800080'; // Purple (default)
                }
            };
            
            // Get simulated traffic data
            const trafficLevel = simulateTrafficData();
            const trafficColor = getTrafficColor(trafficLevel);
            
            // Add the route to the map with traffic-based coloring
            routeLine = L.polyline(routeCoordinates, {
                color: trafficColor,
                weight: 8,
                dashArray: '10, 10',
                dashOffset: '0'
            }).addTo(map);
            
            // Calculate approximate distance in kilometers
            const p1 = L.latLng(routeCoordinates[0]);
            const p2 = L.latLng(routeCoordinates[1]);
            const distanceInKm = (p1.distanceTo(p2) / 1000).toFixed(1);
            
            // Add popup to the middle of the route with traffic info
            const midPoint = [
                (originLatLng.lat + destLatLng.lat) / 2,
                (originLatLng.lng + destLatLng.lng) / 2
            ];
            
            L.popup()
                .setLatLng(midPoint)
                .setContent(`
                    <b>Distance:</b> ${distanceInKm} km<br>
                    <b>Traffic:</b> <span style="color:${trafficColor}">${trafficLevel.replace('-', ' ')}</span>
                `)
                .openOn(map);
            
            // Animate the dash pattern for a moving effect
            let dashOffset = 0;
            function animateDashArray() {
                dashOffset = (dashOffset + 1) % 20;
                routeLine.setStyle({ dashOffset: String(dashOffset) });
                requestAnimationFrame(animateDashArray);
            }
            animateDashArray();
            
            // Fit the map to show the entire route
            const bounds = L.latLngBounds(routeCoordinates);
            map.fitBounds(bounds, { padding: [50, 50] });
        }
        
        // Add traffic flow visualization controls
        const trafficFlowControl = document.createElement('div');
        trafficFlowControl.className = 'traffic-flow-control';
        trafficFlowControl.innerHTML = `
            <div class="traffic-legend">
                <h4>Traffic Flow</h4>
                <div class="flow-item"><span class="flow-color free-flow"></span>Free flow</div>
                <div class="flow-item"><span class="flow-color slow"></span>Slow</div>
                <div class="flow-item"><span class="flow-color queuing"></span>Queuing</div>
                <div class="flow-item"><span class="flow-color stationary"></span>Stationary</div>
                <div class="flow-item"><span class="flow-color closed"></span>Road closed</div>
            </div>
        `;
        document.querySelector('.map-container').appendChild(trafficFlowControl);
        
        // If route points are provided, create the route visualization
        if (routePoints && routePoints.length > 0) {
            const firstPoint = routePoints[0];
            const lastPoint = routePoints[routePoints.length - 1];
            
            // Add markers for origin and destination from API response
            const apiOriginMarker = L.marker([firstPoint.lat, firstPoint.lon], {icon: originIcon})
                .addTo(map)
                .bindPopup("Origin")
                .openPopup();
            
            const apiDestinationMarker = L.marker([lastPoint.lat, lastPoint.lon], {icon: destinationIcon})
                .addTo(map)
                .bindPopup("Destination");
            
            // Create a route line
            const routeCoordinates = routePoints.map(point => [point.lat, point.lon]);
            
            // Add route outline (shadow effect)
            const apiRouteOutline = L.polyline(routeCoordinates, {
                color: '#000',
                weight: 12,
                opacity: 0.4
            }).addTo(map);
            
            // Add the route to the map with popup showing distance
            const apiRouteLine = L.polyline(routeCoordinates, {
                color: '#800080', // Purple
                weight: 8,
                dashArray: '10, 10',
                dashOffset: '0'
            }).addTo(map);
            
            // Calculate approximate distance in kilometers
            let totalDistance = 0;
            for (let i = 0; i < routeCoordinates.length - 1; i++) {
                const p1 = L.latLng(routeCoordinates[i]);
                const p2 = L.latLng(routeCoordinates[i + 1]);
                totalDistance += p1.distanceTo(p2);
            }
            
            // Convert to kilometers and round to one decimal place
            const distanceInKm = (totalDistance / 1000).toFixed(1);
            
            // Add popup to the middle of the route
            const midPointIndex = Math.floor(routeCoordinates.length / 2);
            const midPoint = routeCoordinates[midPointIndex];
            L.popup()
                .setLatLng(midPoint)
                .setContent(`<b>Distance:</b> ${distanceInKm} km`)
                .openOn(map);
            
            // Animate the dash pattern for a moving effect
            let dashOffset = 0;
            function animateDashArray() {
                dashOffset = (dashOffset + 1) % 20;
                apiRouteLine.setStyle({ dashOffset: String(dashOffset) });
                requestAnimationFrame(animateDashArray);
            }
            animateDashArray();
            
            // Fit the map to show the entire route
            const bounds = L.latLngBounds(routeCoordinates);
            map.fitBounds(bounds, { padding: [50, 50] });
            
            // Update input fields with the locations
            if (firstPoint.name) document.getElementById('origin').value = firstPoint.name;
            if (lastPoint.name) document.getElementById('destination').value = lastPoint.name;
        }
    }
    
    /**
     * Function to initialize autocomplete for input fields with Indian locations
     * @param {HTMLElement} inputElement - The input element to add autocomplete to
     */
    function initializeAutocomplete(inputElement) {
        // Remove any existing change event listeners to prevent map reinitialization
        inputElement.onchange = null;
        // List of major Indian cities and locations
        const indianLocations = [
            'Mumbai, Maharashtra', 'Delhi', 'Bangalore, Karnataka', 'Hyderabad, Telangana', 
            'Chennai, Tamil Nadu', 'Kolkata, West Bengal', 'Pune, Maharashtra', 'Ahmedabad, Gujarat', 
            'Jaipur, Rajasthan', 'Lucknow, Uttar Pradesh', 'Kanpur, Uttar Pradesh', 'Nagpur, Maharashtra',
            'Indore, Madhya Pradesh', 'Thane, Maharashtra', 'Bhopal, Madhya Pradesh', 'Visakhapatnam, Andhra Pradesh',
            'Patna, Bihar', 'Vadodara, Gujarat', 'Ghaziabad, Uttar Pradesh', 'Ludhiana, Punjab',
            'Agra, Uttar Pradesh', 'Nashik, Maharashtra', 'Faridabad, Haryana', 'Meerut, Uttar Pradesh',
            'Rajkot, Gujarat', 'Varanasi, Uttar Pradesh', 'Srinagar, Jammu and Kashmir', 'Aurangabad, Maharashtra',
            'Dhanbad, Jharkhand', 'Amritsar, Punjab', 'Navi Mumbai, Maharashtra', 'Allahabad, Uttar Pradesh',
            'Ranchi, Jharkhand', 'Howrah, West Bengal', 'Coimbatore, Tamil Nadu', 'Jabalpur, Madhya Pradesh',
            'Gwalior, Madhya Pradesh', 'Vijayawada, Andhra Pradesh', 'Jodhpur, Rajasthan', 'Madurai, Tamil Nadu',
            'Raipur, Chhattisgarh', 'Kochi, Kerala', 'Chandigarh', 'Guwahati, Assam', 'Bhubaneswar, Odisha',
            'Dehradun, Uttarakhand', 'Mysore, Karnataka', 'Puducherry', 'Thiruvananthapuram, Kerala', 'Shimla, Himachal Pradesh'
        ];
        
        // Create a datalist element
        const datalistId = inputElement.id + '-list';
        let datalist = document.getElementById(datalistId);
        
        // If datalist doesn't exist, create it
        if (!datalist) {
            datalist = document.createElement('datalist');
            datalist.id = datalistId;
            document.body.appendChild(datalist);
            
            // Add options to datalist
            indianLocations.forEach(location => {
                const option = document.createElement('option');
                option.value = location;
                datalist.appendChild(option);
            });
            
            // Connect input to datalist
            inputElement.setAttribute('list', datalistId);
        }
        
        // Add input event listener for custom filtering
        inputElement.addEventListener('input', function() {
            const inputValue = this.value.toLowerCase();
            
            // Clear existing options
            datalist.innerHTML = '';
            
            // Filter locations based on input
            const filteredLocations = indianLocations.filter(location => 
                location.toLowerCase().includes(inputValue)
            );
            
            // Add filtered options to datalist
            filteredLocations.forEach(location => {
                const option = document.createElement('option');
                option.value = location;
                datalist.appendChild(option);
            });
        });
    }
});


/**
 * Function to plan a trip using coordinates selected from the map
 * @param {L.LatLng} originLatLng - The origin coordinates
 * @param {L.LatLng} destLatLng - The destination coordinates
 */
// MODIFIED: Updated planTripWithCoordinates to include new form data (line 620-640) 
function planTripWithCoordinates(originLatLng, destLatLng) {
    console.log('Planning trip with coordinates:', originLatLng, destLatLng);
    
    // Show loading state
    const planTripBtn = document.getElementById('plan-trip-btn');
    planTripBtn.innerHTML = '<span class="loading-text">Processing...</span>';
    planTripBtn.disabled = true;
    planTripBtn.classList.add('loading');
    
    // Get the results section
    const resultsSection = document.getElementById('results');
    
    // MODIFIED: Include new form data in API call
    fetch('http://localhost:5000/api/plan-trip', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            origin: document.getElementById('origin').value,
            destination: document.getElementById('destination').value,
            preferred_date: document.getElementById('preferred-date').value, // ADDED
            preferred_time: document.getElementById('preferred-time').value, // ADDED
            route_preference: document.getElementById('route-preference').value, // ADDED
            origin_lat: originLatLng.lat,
            origin_lon: originLatLng.lng,
            dest_lat: destLatLng.lat,
            dest_lon: destLatLng.lng
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Update the UI with the results
        updateResultsFromRouteData(data);
        
        // Reset button
        planTripBtn.innerHTML = 'Plan My Trip';
        planTripBtn.disabled = false;
        planTripBtn.classList.remove('loading');
        
        // Show the results section
        resultsSection.style.display = 'block';
        resultsSection.classList.add('visible');
    })
    .catch(error => {
        console.error('Error planning trip with coordinates:', error);
        alert('Error planning trip. Please try again.');
        
        // Reset button
        planTripBtn.innerHTML = 'Plan My Trip';
        planTripBtn.disabled = false;
        planTripBtn.classList.remove('loading');
    });
}

/**
 * Update results from route data
 * @param {Object} data - The route data
 */
function updateResultsFromRouteData(data) {
    const bestRouteElement = document.getElementById('best-route');
    const travelTimeElement = document.getElementById('travel-time');
    const departureTimeElement = document.getElementById('departure-time');
    const aiAnalysisElement = document.getElementById('ai-analysis');
    
    // Update best route
    bestRouteElement.textContent = `${document.getElementById('origin').value} to ${document.getElementById('destination').value}`;
    
    // Update travel time
    travelTimeElement.textContent = data.travel_time || 'Not available';
    
    // Update departure time (use current time as a placeholder)
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const formattedHours = hours % 12 || 12;
    const formattedMinutes = minutes < 10 ? '0' + minutes : minutes;
    departureTimeElement.textContent = `${formattedHours}:${formattedMinutes} ${ampm}`;
    
    // Update AI analysis with a placeholder
    aiAnalysisElement.innerHTML = `
        <div class="analysis-section">
            <h4>Traffic Analysis</h4>
            <p>Based on current traffic conditions, this route has moderate congestion.</p>
        </div>
        <div class="analysis-section">
            <h4>Recommended Departure</h4>
            <p>For optimal travel time, consider departing now or after 7:00 PM.</p>
        </div>
    `;
    
    // Update the map with the route points
    if (data.route_points) {
        updateMap(data.route_points);
    }
}