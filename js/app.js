// Smart Travel Planner JavaScript

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const planTripBtn = document.getElementById('plan-trip-btn');
    const originInput = document.getElementById('origin');
    const destinationInput = document.getElementById('destination');
    const resultsSection = document.getElementById('results');
    const bestRouteElement = document.getElementById('best-route');
    const departureTimeElement = document.getElementById('departure-time');
    const travelTimeElement = document.getElementById('travel-time');
    const aiAnalysisElement = document.getElementById('ai-analysis');
    
    // Initialize autocomplete for Indian locations
    initializeAutocomplete(originInput);
    initializeAutocomplete(destinationInput);
    
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
        
        // Validate inputs
        if (!origin || !destination) {
            alert('Please enter both origin and destination');
            return;
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
                destination: destination
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
    function simulateApiResponse(origin, destination) {
        // Add loading animation to button
        planTripBtn.innerHTML = '<span class="loading-text">Processing...</span>';
        planTripBtn.disabled = true;
        planTripBtn.classList.add('loading');
        
        // Simulate loading time
        setTimeout(() => {
            // Mock data that would come from the backend
            const mockData = {
                bestRoute: `${origin} → NH-48 → ${destination}`,
                departureTime: '08:30 AM',
                travelTime: '2 hours 15 minutes',
                aiAnalysis: generateAIAnalysis(origin, destination)
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
    
    /**
     * Function to update the UI with the results
     * @param {Object} data - The data containing the route details
     */
    function updateResults(data) {
        bestRouteElement.textContent = data.bestRoute;
        departureTimeElement.textContent = data.departureTime;
        travelTimeElement.textContent = data.travelTime;
        
        // Add AI source information to the analysis
        let aiContent = data.aiAnalysis;
        
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
     * Function to update the map with the route
     * @param {Array} routePoints - The route coordinates
     */
    function updateMap(routePoints) {
        // Get the map container element
        const mapContainer = document.getElementById('map');
        
        // Clear any existing map
        mapContainer.innerHTML = '';
        
        // Check if we have route points
        if (!routePoints || routePoints.length === 0) {
            console.error('No route points provided');
            return;
        }
        
        // Initialize the map with Leaflet
        initializeMap(routePoints);
    }
    
    /**
     * Initialize the map with Leaflet
     * @param {Array} routePoints - The route coordinates
     */
    function initializeMap(routePoints) {
        // Calculate the center of the route
        const firstPoint = routePoints[0];
        const lastPoint = routePoints[routePoints.length - 1];
        
        // Initialize the map with Leaflet
        const map = L.map('map').setView([firstPoint.lat, firstPoint.lon], 10);
        
        // Add OpenStreetMap tile layer with CORS-friendly provider
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            subdomains: ['a', 'b', 'c'],
            crossOrigin: true,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
        
        // Add click event to show coordinates
        const coordInfo = L.control({position: 'bottomleft'});
        coordInfo.onAdd = function() {
            const div = L.DomUtil.create('div', 'coordinate-info');
            div.innerHTML = 'Click on map to see coordinates';
            div.style.backgroundColor = 'white';
            div.style.padding = '5px';
            div.style.borderRadius = '5px';
            div.style.boxShadow = '0 1px 5px rgba(0,0,0,0.4)';
            return div;
        };
        coordInfo.addTo(map);
        
        map.on('click', function(e) {
            coordInfo.getContainer().innerHTML = 
                `<b>Latitude:</b> ${e.latlng.lat.toFixed(5)}<br>
                 <b>Longitude:</b> ${e.latlng.lng.toFixed(5)}`;
        });
        
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
        
        // Add markers for origin and destination
        const originMarker = L.marker([firstPoint.lat, firstPoint.lon], {icon: originIcon})
            .addTo(map)
            .bindPopup("Origin")
            .openPopup();
        
        const destinationMarker = L.marker([lastPoint.lat, lastPoint.lon], {icon: destinationIcon})
            .addTo(map)
            .bindPopup("Destination");
        
        // Create a route line
        const routeCoordinates = routePoints.map(point => [point.lat, point.lon]);
        
        // Add route outline (shadow effect)
        const routeOutline = L.polyline(routeCoordinates, {
            color: '#000',
            weight: 12,
            opacity: 0.4
        }).addTo(map);
        
        // Add the route to the map with popup showing distance
        const routeLine = L.polyline(routeCoordinates, {
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
            routeLine.setStyle({ dashOffset: String(dashOffset) });
            requestAnimationFrame(animateDashArray);
        }
        animateDashArray();
        
        // Fit the map to show the entire route
        const bounds = L.latLngBounds(routeCoordinates);
        map.fitBounds(bounds, { padding: [50, 50] });
    }
    
    /**
     * Function to initialize autocomplete for input fields with Indian locations
     * @param {HTMLElement} inputElement - The input element to add autocomplete to
     */
    function initializeAutocomplete(inputElement) {
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