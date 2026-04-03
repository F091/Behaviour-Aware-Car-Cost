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
    # Hybrid vehicles don't have traditional engine sizes, so they use "any"
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
    
    # If fuel type is not recognised, raise an error
    raise ValueError(f"Unknown fuel type: {fuel_type}")


def calculate_behaviour_adjustment(
    city_ratio: int,
    driving_style: str,
    short_trip_frequency: str
) -> float:
    """
    Calculate how much behaviour factors reduce the baseline MPG.
    
    This function applies simple behaviour-based adjustments to fuel efficiency.
    Poor driving conditions and habits result in lower MPG (higher fuel costs).
    
    All adjustments are applied together as multipliers on the baseline MPG.
    
    Args:
        city_ratio: Percentage of driving in city (0-100). City driving reduces MPG.
        driving_style: One of "calm", "normal", or "brisk". More aggressive = lower MPG.
        short_trip_frequency: One of "low", "medium", or "high". More short trips = lower MPG.
        
    Returns:
        A multiplier to apply to baseline MPG (e.g., 0.85 means 15% reduction)
        
    Raises:
        ValueError: If city_ratio is not between 0 and 100
    """
    # Validate that city_ratio is within the valid range
    if city_ratio < 0 or city_ratio > 100:
        raise ValueError("city_ratio must be between 0 and 100")
    
    # Start with the baseline multiplier (no reduction)
    multiplier = 1.0
    
    # Apply city ratio reduction
    # Linear reduction from 0% to 15% based on city_ratio (0 to 100)
    # At 0% city driving, no reduction. At 100% city driving, 15% reduction.
    city_reduction = (city_ratio / 100) * 0.15
    city_multiplier = 1.0 - city_reduction
    
    # Apply driving style reduction
    if driving_style.lower() == "calm":
        driving_multiplier = 1.0  # No reduction
    elif driving_style.lower() == "normal":
        driving_multiplier = 0.95  # 5% reduction
    elif driving_style.lower() == "brisk":
        driving_multiplier = 0.88  # 12% reduction
    else:
        raise ValueError(f"Unknown driving style: {driving_style}")
    
    # Apply short trip frequency reduction
    if short_trip_frequency.lower() == "low":
        trip_multiplier = 1.0  # No reduction
    elif short_trip_frequency.lower() == "medium":
        trip_multiplier = 0.95  # 5% reduction
    elif short_trip_frequency.lower() == "high":
        trip_multiplier = 0.90  # 10% reduction
    else:
        raise ValueError(f"Unknown short trip frequency: {short_trip_frequency}")
    
    # Multiply all the factors together to get the total adjustment
    multiplier = city_multiplier * driving_multiplier * trip_multiplier
    
    return multiplier


def estimate_monthly_fuel_cost(
    fuel_type: str,
    engine_capacity_cc: int,
    annual_mileage: int,
    fuel_price_per_litre: float,
    city_ratio: int = 0,
    driving_style: str = "normal",
    short_trip_frequency: str = "low"
) -> float:
    """
    Estimate the monthly fuel cost for a vehicle with behaviour adjustments.
    
    This function calculates how much fuel a vehicle will use per month based on
    its fuel type, engine size, and annual mileage. It then applies behaviour-based
    adjustments (city driving, driving style, short trips) that reduce fuel efficiency.
    Finally, it multiplies the adjusted fuel usage by the current fuel price.
    
    Args:
        fuel_type: The fuel type ("petrol", "diesel", or "hybrid")
        engine_capacity_cc: The engine capacity in cubic centimetres
        annual_mileage: The expected annual mileage in miles
        fuel_price_per_litre: The current fuel price in pounds per litre
        city_ratio: Percentage of driving in city areas (0-100). Default is 0.
        driving_style: One of "calm", "normal", or "brisk". Default is "normal".
        short_trip_frequency: One of "low", "medium", or "high". Default is "low".
        
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
    
    # Calculate the behaviour adjustment multiplier
    behaviour_multiplier = calculate_behaviour_adjustment(
        city_ratio,
        driving_style,
        short_trip_frequency
    )
    
    # Apply the behaviour adjustment to the baseline MPG
    # Lower multiplier means lower MPG (worse fuel efficiency)
    adjusted_mpg = baseline_mpg * behaviour_multiplier

    if adjusted_mpg <= 0:
        raise ValueError("Adjusted MPG must be greater than zero")
    
    # Calculate monthly mileage from annual mileage
    monthly_mileage = annual_mileage / 12
   
    # Calculate how many gallons of fuel will be used per month
    # Formula: monthly_mileage / MPG = gallons used
    gallons_per_month = monthly_mileage / adjusted_mpg
    
    # Convert gallons to litres
    # 1 imperial gallon = 4.54609 litres
    litres_per_month = gallons_per_month * 4.54609
    
    # Calculate the monthly cost
    # Cost = litres per month * price per litre
    monthly_cost = litres_per_month * fuel_price_per_litre
    
    # Return the cost rounded to 2 decimal places (pence level)
    return round(monthly_cost, 2)