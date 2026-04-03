# DRIVEWISE - Car Ownership Cost Estimator

## Overview

DRIVEWISE is a web application that estimates monthly car ownership costs based on vehicle details and driving habits. The system uses the DVLA API to look up real vehicle data and applies behaviour-aware multipliers to calculate realistic fuel and maintenance costs.

### How it Works

Users enter:
- Vehicle registration number (looked up via DVLA API)
- Annual mileage and fuel price
- Driving profile (city ratio, driving style, short trip frequency)

The system returns:
- Monthly fuel and maintenance costs
- Detailed cost breakdown
- Visual cost charts
- Exportable results as JSON

## Running the Application

### Prerequisites

```bash
pip install fastapi uvicorn requests pydantic
```

### Set the DVLA API Key (Optional)

If you have a DVLA VES API key:
```bash
export DVLA_API_KEY='your_api_key_here'
```

Without the key, the system uses mock data (50 test vehicles).

### Start the Backend

```bash
python -m uvicorn backend.app.main:app --reload
```

The API will run at `http://127.0.0.1:8000`

### Open the Frontend

Use a local HTTP server:
```bash
cd frontend
python -m http.server 8000
```
Then visit: `http://localhost:8000`

## Project Structure

- **backend/** - FastAPI application, vehicle lookup, cost calculations
- **frontend/** - HTML, CSS, JavaScript for the web interface
- **rules/** - JSON rules for fuel efficiency and maintenance costs
- **docs/** - Architecture, requirements, and development log

## Testing

Try these vehicle registrations with mock data:
- AB21ABC (Toyota Corolla, Petrol)
- CD22CDE (Ford Focus, Diesel)
- GH24GHI (Toyota Prius, Hybrid)
- EF36EFG (Toyota RAV4, Hybrid)

Or see all 50 vehicles in `backend/mock_data/dvla_example.json`

## API Endpoints

- `GET /vehicle/{registration}` - Get vehicle details
- `GET /estimate/fuel/{registration}` - Estimate fuel costs
- `GET /estimate/ownership/{registration}` - Full cost breakdown
- `GET /docs` - Interactive API documentation (Swagger UI)

## Key Features

✓ Real DVLA API integration with mock data fallback
✓ Behaviour-aware cost multipliers (driving style, city ratio, short trips)
✓ Transparent rule-based calculations
✓ Visual charts (Chart.js)
✓ Responsive design (mobile, tablet, desktop)
✓ Export results as JSON
✓ No ML/AI - fully explainable logic

## Future Improvements

- Depreciation calculation
- Insurance cost integration
- MOT and tax costs
- User accounts and history tracking

---

Repository: https://github.com/F091/Behaviour-Aware-Car-Cost