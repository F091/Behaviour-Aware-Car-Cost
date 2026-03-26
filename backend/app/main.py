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


class MaintenanceBreakdown(BaseModel):
    """
    A breakdown of monthly maintenance costs by category.
    
    This shows how the total maintenance reserve is distributed across
    different types of maintenance work.
    """
    service_monthly: float
    tyres_monthly: float
    brakes_monthly: float
    major_service_monthly: float


class FuelExplanation(BaseModel):
    """
    Explanation of the behaviour factors affecting fuel cost.
    
    This shows the driving parameters that were used to adjust the
    baseline fuel efficiency estimate.
    """
    city_ratio: int
    driving_style: str
    short_trip_frequency: str


class OwnershipCostEstimateResponse(BaseModel):
    """
    Response model for the full ownership cost estimation endpoint.
    
    This contains the vehicle details along with estimated monthly costs for
    fuel and maintenance, plus the total monthly running cost and explanatory
    information about why the costs are what they are.
    """
    registration: str
    make: str
    model: str
    fuel_type: str
    engine_capacity_cc: int
    estimated_monthly_fuel_cost: float
    estimated_monthly_maintenance_cost: float
    total_monthly_running_cost: float
    maintenance_breakdown: MaintenanceBreakdown
    fuel_explanation: FuelExplanation
    insight_summary: str


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


def calculate_maintenance_breakdown(
    engine_capacity_cc: int,
    annual_mileage: int,
    city_ratio: int,
    driving_style: str,
    short_trip_frequency: str
) -> tuple:
    """
    Helper function to calculate individual maintenance cost components.
    
    This function breaks down the total maintenance cost into its constituent
    parts so we can show users where their maintenance money is going.
    
    Returns a tuple of (service_monthly, tyres_monthly, brakes_monthly, major_service_monthly)
    """
    import json
    from pathlib import Path
    from backend.services.maintenance_engine import get_engine_band
    
    # Load the maintenance rules
    rules_path = Path(__file__).parent.parent.parent / "rules" / "maintenance.json"
    with open(rules_path, "r") as file:
        rules = json.load(file)
    
    # Get multipliers
    engine_band = get_engine_band(engine_capacity_cc)
    engine_multiplier = rules["engine_cost_multipliers"][engine_band]
    driving_multiplier = rules["driving_style_wear_multipliers"][driving_style.lower()]
    short_trip_multiplier = rules["short_trip_wear_multipliers"][short_trip_frequency.lower()]
    
    # Calculate brake multiplier
    city_brake_max = rules["city_ratio_brake_multiplier_max"]
    brake_city_multiplier = 1.0 + ((city_ratio / 100) * (city_brake_max - 1.0))
    
    # 1. Service
    service_interval_months = rules["service"]["interval_months"]
    service_cost = rules["service"]["base_cost"]
    service_monthly = (service_cost * engine_multiplier) / service_interval_months
    
    # 2. Tyres
    tyre_interval_miles = rules["tyres"]["base_interval_miles"]
    tyre_cost = rules["tyres"]["base_cost"]
    tyre_replacements_per_year = annual_mileage / tyre_interval_miles
    tyre_yearly_cost = tyre_replacements_per_year * tyre_cost * engine_multiplier * short_trip_multiplier
    tyres_monthly = tyre_yearly_cost / 12
    
    # 3. Brakes
    brake_interval_miles = rules["brakes"]["base_interval_miles"]
    brake_cost = rules["brakes"]["base_cost"]
    brake_replacements_per_year = annual_mileage / brake_interval_miles
    brake_yearly_cost = (
        brake_replacements_per_year * 
        brake_cost * 
        engine_multiplier * 
        driving_multiplier * 
        brake_city_multiplier
    )
    brakes_monthly = brake_yearly_cost / 12
    
    # 4. Major service
    major_interval_miles = rules["major_service"]["base_interval_miles"]
    major_cost = rules["major_service"]["base_cost"]
    major_services_per_year = annual_mileage / major_interval_miles
    major_yearly_cost = (
        major_services_per_year * 
        major_cost * 
        engine_multiplier * 
        driving_multiplier
    )
    major_service_monthly = major_yearly_cost / 12
    
    return (
        round(service_monthly, 2),
        round(tyres_monthly, 2),
        round(brakes_monthly, 2),
        round(major_service_monthly, 2)
    )


def generate_insight_summary(
    city_ratio: int,
    driving_style: str,
    short_trip_frequency: str,
    fuel_cost: float,
    maintenance_cost: float
) -> str:
    """
    Generate a human-readable insight about why costs are higher or lower.
    
    This function creates a simple text explanation of the behaviour factors
    and how they affect the estimated ownership costs.
    """
    insights = []
    
    # Check driving style
    if driving_style.lower() == "brisk":
        insights.append("brisk driving increases wear on brakes and tyres")
    elif driving_style.lower() == "calm":
        insights.append("calm driving reduces wear on engine and brakes")
    
    # Check short trip frequency
    if short_trip_frequency.lower() == "high":
        insights.append("frequent short trips increase overall component wear")
    
    # Check city ratio
    if city_ratio > 75:
        insights.append("high city driving increases brake wear significantly")
    elif city_ratio > 50:
        insights.append("moderate city driving increases maintenance costs")
    elif city_ratio == 0:
        insights.append("highway-only driving reduces brake wear")
    
    # Check if fuel dominates costs
    if fuel_cost > maintenance_cost:
        insights.append("fuel costs dominate total running costs")
    
    # Build the summary
    if insights:
        summary = "Cost factors: " + ", ".join(insights) + "."
    else:
        summary = "Standard driving conditions with baseline costs."
    
    return summary


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
    
    This endpoint calculates complete monthly ownership cost, including both
    fuel and maintenance costs. It accounts for the vehicle's engine size, driving
    habits, and driving conditions. The response includes a breakdown of maintenance
    costs and an explanation of the behaviour factors affecting the estimate.
    
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
    
    # Calculate the maintenance breakdown
    (service_monthly, tyres_monthly, brakes_monthly, major_service_monthly) = (
        calculate_maintenance_breakdown(
            engine_capacity_cc=vehicle.engine_capacity_cc,
            annual_mileage=annual_mileage,
            city_ratio=city_ratio,
            driving_style=driving_style,
            short_trip_frequency=short_trip_frequency
        )
    )
    
    # Generate insight summary
    insight = generate_insight_summary(
        city_ratio=city_ratio,
        driving_style=driving_style,
        short_trip_frequency=short_trip_frequency,
        fuel_cost=fuel_cost,
        maintenance_cost=maintenance_cost
    )
    
    # Calculate the total monthly running cost
    total_cost = round(fuel_cost + maintenance_cost, 2)
    
    # Build and return the response
    return OwnershipCostEstimateResponse(
        registration=vehicle.registration,
        make=vehicle.make,
        model=vehicle.model,
        fuel_type=vehicle.fuel_type,
        engine_capacity_cc=vehicle.engine_capacity_cc,
        estimated_monthly_fuel_cost=fuel_cost,
        estimated_monthly_maintenance_cost=maintenance_cost,
        total_monthly_running_cost=total_cost,
        maintenance_breakdown=MaintenanceBreakdown(
            service_monthly=service_monthly,
            tyres_monthly=tyres_monthly,
            brakes_monthly=brakes_monthly,
            major_service_monthly=major_service_monthly
        ),
        fuel_explanation=FuelExplanation(
            city_ratio=city_ratio,
            driving_style=driving_style,
            short_trip_frequency=short_trip_frequency
        ),
        insight_summary=insight
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