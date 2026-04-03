## Week 1 – 10 Feb 2026
- Initialised repository structure (backend/frontend/rules/docs)
- Created placeholders for rules, mock data, connectors, and documentation
- Submitted DVLA VES and DVSA MOT API access requests
- Next: define requirements + architecture, then build MVP with mock data
- Received DVLA VES API key and configured local environment variable
- Received DVSA MOT API credentials and documented environment variables

## Week 2 – 17 Feb 2026
- Defined Vehicle Pydantic model with fields: registration, make, model, year, fuel_type, engine_capacity_cc
- Created backend/domain/vehicle.py with proper type hints
- Drafted architecture documentation outlining service layer pattern
- Decided to use rule-based cost estimation (no ML) for transparency and explainability
- Began design of fuel efficiency rules JSON structure
- Next: implement connector layer and mock data loader

## Week 3 – 24 Feb 2026
- Created backend/connectors/dvla_client.py with mock data loader function
- Built backend/mock_data/dvla_example.json with 4 initial test vehicles
- Implemented backend/services/vehicle_service.py wrapper around connector
- Started fuel_efficiency.json with baseline MPG by fuel type and engine band
- Tested mock vehicle lookup with curl commands
- Next: implement fuel cost engine and begin API structure

## Week 4 – 3 Mar 2026
- Implemented backend/services/cost_engine.py for fuel cost estimation
- Added behaviour multipliers: city_ratio (0-100%), driving_style (calm/normal/brisk), short_trip_frequency (low/medium/high)
- Integrated engine band classification (0-1400cc, 1400-2000cc, 2000-3000cc, 3000+cc)
- Created fuel_efficiency.json with realistic MPG baselines for petrol, diesel, hybrid
- Implemented cost validation and rounding to 2 decimal places
- Next: build maintenance cost engine and FastAPI endpoints

## Week 5 – 10 Mar 2026
- Implemented backend/services/maintenance_engine.py with component-based costing
- Added cost components: service (12 monthly intervals), tyres (25k mile intervals), brakes (30k miles), major service (60k miles)
- Created maintenance.json with realistic interval costs and multipliers
- Implemented engine size multiplier (0.8–1.6x) and city brake wear adjustment
- Tested calculations with mock vehicles
- Next: create FastAPI application endpoints and enable CORS

## Week 6 – 17 Mar 2026
- Built backend/app/main.py with FastAPI application
- Created three main endpoints: /vehicle, /estimate/fuel, /estimate/ownership
- Added CORSMiddleware to enable frontend-backend communication
- Implemented calculate_maintenance_breakdown() helper function
- Implemented generate_insight_summary() function for driving profile analysis
- Tested endpoints via Swagger UI at http://127.0.0.1:8000/docs
- Resolved CORS issues with frontend fetch calls
- Next: build frontend form and results display

## Week 7 – 24 Mar 2026
- Created frontend/index.html with three-screen SPA structure (landing, form, results)
- Built frontend/style.css with full responsive design and landing page car animation
- Implemented frontend/script.js with form validation and API integration
- Added handleEnter() for landing page animation sequence
- Implemented handleCalculate() with form validation and API fetch
- Created displayResults() function to populate results from API response
- Tested form → API → results workflow end-to-end
- All existing functionality working without breaking changes
- Next: improve results screen layout with charts and export functionality

## Week 8 – 31 Mar 2026
- Expanded backend/mock_data/dvla_example.json to 50 realistic UK vehicles
- Added vehicles across all engine size categories (1.0L to 8.0L)
- Included diverse fuel types: petrol, diesel, hybrid, electric
- Replaced mock DVLA connector with real DVLA VES API integration
- Implemented fallback to mock data if API fails or returns 404
- Modified backend/connectors/dvla_client.py to support both real API and mock fallback
- Added safe fuel type mapping (electric/hybrid → hybrid, diesel stays diesel, others → petrol)
- Tested API integration with actual DVLA endpoint
- System continues to function reliably with or without API key
- Next: enhance results presentation and prepare for submission

## Week 9 – 1 Apr 2026
- Restructured results screen HTML layout into 2-column responsive grid
- Added Chart.js integration (CDN) for data visualization
- Implemented doughnut chart for fuel vs maintenance cost breakdown
- Implemented horizontal bar chart for maintenance item details (service, tyres, brakes, major service)
- Created export functionality to download results as JSON
- Added "New Search" button for user workflow continuity
- Updated CSS with comprehensive styling for chart cards and results grid
- Enhanced responsive design for mobile, tablet, and desktop viewports
- All existing API calls preserved; no breaking changes to backend
- System now provides clear visual representation of cost estimates
- Incremental commits maintained throughout development
- Next: final testing and documentation updates

