# backend/services/cost_engine.py

import json
from pathlib import Path


def get_engine_band(fuel_type: str, engine_capacity_cc: int) -> str:
    """
    Determine the engine capacity band for a given fuel type and engine size.
    
    Engine capacity bands differ slightly between fuel types. This function
    returns the band name (e.g., "0-1400") that the engine falls into.
    
    Args:
        fuel_type: The fuel type ("petrol", "diesel", or "hybrid")
        engine_capacity_cc: The engine capacity in cubic centimetres (cc)
        
    Returns:
        A string representing the engine band (e.g., "1400-2000")
    """
    # For now, hybrid vehhicles use a single "any" efficiency band
    if fuel_type.lower() == "hybrid":
        return "any"
    
    # Get the numeric value of engine capacity
    capacity = engine_capacity_cc
    
    # Determine the band based on fuel type
    if fuel_type.lower() == "petrol":
        if capacity <= 1400:
            return "0-1400"
        elif capacity <= 2000:
            return "1400-2000"
        elif capacity <= 3000:
            return "2000-3000"
        else:
            return "3000+"
    
    elif fuel_type.lower() == "diesel":
        if capacity <= 1400:
            return "0-1400"
        elif capacity <= 2000:
            return "1400-2000"
        elif capacity <= 3000:
            return "2000-3000"
        else:
            return "3000+"
    
    # If fuel type is not recognized, raise an error
    raise ValueError(f"Unknown fuel type: {fuel_type}")


def estimate_monthly_fuel_cost(
    fuel_type: str,
    engine_capacity_cc: int,
    annual_mileage: int,
    fuel_price_per_litre: float
) -> float:
    """
    Estimate the monthly fuel cost for a vehicle.
    
    This function calculates how much fuel a vehicle will use per month based on
    its fuel type, engine size, and annual mileage. It then multiplies this by
    the current fuel price to get an estimated monthly cost.
    
    Args:
        fuel_type: The fuel type ("petrol", "diesel", or "hybrid")
        engine_capacity_cc: The engine capacity in cubic centimetres
        annual_mileage: The expected annual mileage in miles
        fuel_price_per_litre: The current fuel price in pounds per litre
        
    Returns:
        The estimated monthly fuel cost in pounds, rounded to 2 decimal places
    """
    # Load the fuel efficiency rules from the JSON file
    rules_path = Path(__file__).parent.parent.parent / "rules" / "fuel_efficiency.json"
    with open(rules_path, "r") as file:
        fuel_efficiency_rules = json.load(file)
    
    # Get the engine band for this vehicle
    engine_band = get_engine_band(fuel_type, engine_capacity_cc)
    
    # Get the baseline MPG for this fuel type and engine band
    # MPG means miles per gallon (imperial)
    baseline_mpg = fuel_efficiency_rules[fuel_type.lower()][engine_band]
    
    # Calculate monthly mileage from annual mileage
    monthly_mileage = annual_mileage / 12
    
    # Calculate how many gallons of fuel will be used per month
    # Formula: monthly_mileage / MPG = gallons used
    gallons_per_month = monthly_mileage / baseline_mpg
    
    # Convert gallons to litres
    # 1 imperial gallon = 4.54609 litres
    litres_per_month = gallons_per_month * 4.54609
    
    # Calculate the monthly cost
    # Cost = litres per month * price per litre
    monthly_cost = litres_per_month * fuel_price_per_litre
    
    # Return the cost rounded to 2 decimal places (pence level)
    return round(monthly_cost, 2)