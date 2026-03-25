# backend/app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.services.vehicle_service import get_vehicle
from backend.services.cost_engine import estimate_monthly_fuel_cost
from backend.services.maintenance_engine import estimate_monthly_maintenance_cost


# Create the FastAPI application instance
# This is the web server that will handle HTTP requests
app = FastAPI(
    title="Car Cost System API",
    description="API for vehicle lookup and cost estimation",
    version="0.1.0"
)


class FuelCostEstimateResponse(BaseModel):
    """
    Response model for the fuel cost estimation endpoint.
    
    This contains the vehicle details along with the estimated monthly fuel cost.
    """
    registration: str
    make: str
    model: str
    fuel_type: str
    engine_capacity_cc: int
    estimated_monthly_fuel_cost: float


class OwnershipCostEstimateResponse(BaseModel):
    """
    Response model for the full ownership cost estimation endpoint.
    
    This contains the vehicle details along with estimated monthly costs for
    fuel and maintenance, plus the total monthly running cost.
    """
    registration: str
    make: str
    model: str
    fuel_type: str
    engine_capacity_cc: int
    estimated_monthly_fuel_cost: float
    estimated_monthly_maintenance_cost: float
    total_monthly_running_cost: float


@app.get("/vehicle/{registration}")
def get_vehicle_endpoint(registration: str):
    """
    Retrieve vehicle details by registration number.
    
    This endpoint takes a registration number as input, calls the vehicle service
    to look up the vehicle, and returns the vehicle details. If the registration
    is not found, it returns a 404 error.
    
    Args:
        registration: The vehicle registration number (e.g., "AB21ABC")
        
    Returns:
        A Vehicle object with the vehicle's details (make, model, year, fuel_type, etc.)
        
    Raises:
        HTTPException: A 404 error if the registration is not found
    """
    try:
        # Call the service to look up the vehicle
        vehicle = get_vehicle(registration)
        return vehicle
    
    except ValueError:
        # If the vehicle is not found, return a 404 error
        raise HTTPException(
            status_code=404,
            detail=f"Vehicle with registration '{registration}' not found"
        )


@app.get("/estimate/fuel/{registration}", response_model=FuelCostEstimateResponse)
def estimate_fuel_cost(
    registration: str,
    annual_mileage: int,
    fuel_price_per_litre: float,
    city_ratio: int = 0,
    driving_style: str = "normal",
    short_trip_frequency: str = "low"
):
    """
    Estimate the monthly fuel cost for a vehicle including behaviour adjustments.
    
    This endpoint takes a vehicle registration, annual mileage, fuel price, and
    behaviour parameters, then calculates the estimated monthly fuel cost based
    on the vehicle's fuel type, engine size, and driving habits.
    
    Args:
        registration: The vehicle registration number (e.g., "AB21ABC")
        annual_mileage: The expected annual mileage in miles
        fuel_price_per_litre: The current fuel price in pounds per litre
        city_ratio: Percentage of driving in city areas (0-100). Default is 0.
        driving_style: One of "calm", "normal", or "brisk". Default is "normal".
        short_trip_frequency: One of "low", "medium", or "high". Default is "low".
        
    Returns:
        A response object containing vehicle details and the estimated monthly fuel cost
        
    Raises:
        HTTPException: A 404 error if the registration is not found
    """
    try:
        # Call the service to look up the vehicle
        vehicle = get_vehicle(registration)
    
    except ValueError:
        # If the vehicle is not found, return a 404 error
        raise HTTPException(
            status_code=404,
            detail=f"Vehicle with registration '{registration}' not found"
        )
    
    # Calculate the estimated monthly fuel cost using the cost engine
    # This includes behaviour-based adjustments
    estimated_cost = estimate_monthly_fuel_cost(
        fuel_type=vehicle.fuel_type,
        engine_capacity_cc=vehicle.engine_capacity_cc,
        annual_mileage=annual_mileage,
        fuel_price_per_litre=fuel_price_per_litre,
        city_ratio=city_ratio,
        driving_style=driving_style,
        short_trip_frequency=short_trip_frequency
    )
    
    # Build and return the response
    return FuelCostEstimateResponse(
        registration=vehicle.registration,
        make=vehicle.make,
        model=vehicle.model,
        fuel_type=vehicle.fuel_type,
        engine_capacity_cc=vehicle.engine_capacity_cc,
        estimated_monthly_fuel_cost=estimated_cost
    )


@app.get("/estimate/ownership/{registration}", response_model=OwnershipCostEstimateResponse)
def estimate_ownership_cost(
    registration: str,
    annual_mileage: int,
    fuel_price_per_litre: float,
    city_ratio: int = 0,
    driving_style: str = "normal",
    short_trip_frequency: str = "low"
):
    """
    Estimate the total monthly running cost for a vehicle.
    
    This endpoint calculates the complete monthly ownership cost, including both
    fuel and maintenance costs. It accounts for the vehicle's engine size, driving
    habits, and driving conditions.
    
    Args:
        registration: The vehicle registration number (e.g., "AB21ABC")
        annual_mileage: The expected annual mileage in miles
        fuel_price_per_litre: The current fuel price in pounds per litre
        city_ratio: Percentage of driving in city areas (0-100). Default is 0.
        driving_style: One of "calm", "normal", or "brisk". Default is "normal".
        short_trip_frequency: One of "low", "medium", or "high". Default is "low".
        
    Returns:
        A response object containing vehicle details and estimated monthly costs
        
    Raises:
        HTTPException: A 404 error if the registration is not found
    """
    try:
        # Call the service to look up the vehicle
        vehicle = get_vehicle(registration)
    
    except ValueError:
        # If the vehicle is not found, return a 404 error
        raise HTTPException(
            status_code=404,
            detail=f"Vehicle with registration '{registration}' not found"
        )
    
    # Calculate the estimated monthly fuel cost
    fuel_cost = estimate_monthly_fuel_cost(
        fuel_type=vehicle.fuel_type,
        engine_capacity_cc=vehicle.engine_capacity_cc,
        annual_mileage=annual_mileage,
        fuel_price_per_litre=fuel_price_per_litre,
        city_ratio=city_ratio,
        driving_style=driving_style,
        short_trip_frequency=short_trip_frequency
    )
    
    # Calculate the estimated monthly maintenance cost
    maintenance_cost = estimate_monthly_maintenance_cost(
        engine_capacity_cc=vehicle.engine_capacity_cc,
        annual_mileage=annual_mileage,
        city_ratio=city_ratio,
        driving_style=driving_style,
        short_trip_frequency=short_trip_frequency
    )
    
    # Calculate the total monthly running cost
    total_cost = fuel_cost + maintenance_cost
    
    # Build and return the response
    return OwnershipCostEstimateResponse(
        registration=vehicle.registration,
        make=vehicle.make,
        model=vehicle.model,
        fuel_type=vehicle.fuel_type,
        engine_capacity_cc=vehicle.engine_capacity_cc,
        estimated_monthly_fuel_cost=fuel_cost,
        estimated_monthly_maintenance_cost=maintenance_cost,
        total_monthly_running_cost=total_cost
    )


@app.get("/health")
def health_check():
    """
    Simple health check endpoint.
    
    This is a basic endpoint that returns a status message. It's useful for
    checking if the API is running and responding correctly.
    
    Returns:
        A simple dictionary with status information
    """
    return {"status": "ok"}


# This allows the app to be run directly with: python -m app.main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)