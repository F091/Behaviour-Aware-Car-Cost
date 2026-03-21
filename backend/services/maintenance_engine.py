# backend/services/maintenance_engine.py

import json
from pathlib import Path


def get_engine_band(engine_capacity_cc: int) -> str:
    """
    Determine the engine capacity band based on engine size.
    
    Engine bands are used to apply cost multipliers. Larger engines
    typically have higher maintenance costs.
    
    Args:
        engine_capacity_cc: The engine capacity in cubic centimetres
        
    Returns:
        A string representing the engine band (e.g., "1400-2000")
    """
    capacity = engine_capacity_cc
    
    if capacity <= 1400:
        return "0-1400"
    elif capacity <= 2000:
        return "1400-2000"
    elif capacity <= 3000:
        return "2000-3000"
    else:
        return "3000+"


def estimate_monthly_maintenance_cost(
    engine_capacity_cc: int,
    annual_mileage: int,
    city_ratio: int,
    driving_style: str,
    short_trip_frequency: str
) -> float:
    """
    Estimate the monthly maintenance reserve for a vehicle.
    
    This function calculates how much a vehicle owner should reserve
    each month for maintenance. It accounts for:
    - Annual servicing
    - Tyre replacements
    - Brake work
    - Major service items
    
    The estimate is adjusted based on engine size, driving behaviour,
    and driving conditions (city ratio).
    
    Args:
        engine_capacity_cc: The engine capacity in cubic centimetres
        annual_mileage: The expected annual mileage in miles
        city_ratio: Percentage of driving in city (0-100)
        driving_style: One of "calm", "normal", or "brisk"
        short_trip_frequency: One of "low", "medium", or "high"
        
    Returns:
        The estimated monthly maintenance reserve in pounds, rounded to 2 decimal places
    """
    # Load the maintenance rules from the JSON file
    rules_path = Path(__file__).parent.parent.parent / "rules" / "maintenance.json"
    with open(rules_path, "r") as file:
        rules = json.load(file)
    
    # Get the engine band and the corresponding cost multiplier
    engine_band = get_engine_band(engine_capacity_cc)
    engine_multiplier = rules["engine_cost_multipliers"][engine_band]
    
    # Get behaviour-based wear multipliers
    driving_multiplier = rules["driving_style_wear_multipliers"][driving_style.lower()]
    short_trip_multiplier = rules["short_trip_wear_multipliers"][short_trip_frequency.lower()]
    
    # Calculate brake wear multiplier based on city driving
    # City driving increases brake wear. The multiplier ranges from 1.0 (0% city)
    # to city_ratio_brake_multiplier_max (100% city)
    city_brake_max = rules["city_ratio_brake_multiplier_max"]
    brake_city_multiplier = 1.0 + ((city_ratio / 100) * (city_brake_max - 1.0))
    
    # Calculate monthly cost for each maintenance item
    
    # 1. Annual service
    # This is a regular service that happens at a fixed interval (in months)
    # Engine size affects the service cost
    service_interval_months = rules["service"]["interval_months"]
    service_cost = rules["service"]["base_cost"]
    service_monthly = (service_cost * engine_multiplier) / service_interval_months  # Apply engine multiplier
    
    # 2. Tyres
    # Calculate how often tyres need replacing based on annual mileage
    tyre_interval_miles = rules["tyres"]["base_interval_miles"]
    tyre_cost = rules["tyres"]["base_cost"]
    # How many times per year does tyre replacement happen?
    tyre_replacements_per_year = annual_mileage / tyre_interval_miles
    # Cost per year adjusted for wear multipliers
    tyre_yearly_cost = tyre_replacements_per_year * tyre_cost * engine_multiplier * short_trip_multiplier
    tyre_monthly = tyre_yearly_cost / 12
    
    # 3. Brakes
    # Calculate how often brake work is needed based on annual mileage
    brake_interval_miles = rules["brakes"]["base_interval_miles"]
    brake_cost = rules["brakes"]["base_cost"]
    # How many times per year does brake work happen?
    brake_replacements_per_year = annual_mileage / brake_interval_miles
    # Cost per year adjusted for engine size, driving style, and city driving
    brake_yearly_cost = (
        brake_replacements_per_year * 
        brake_cost * 
        engine_multiplier * 
        driving_multiplier * 
        brake_city_multiplier
    )
    brake_monthly = brake_yearly_cost / 12
    
    # 4. Major service (timing belt, etc.)
    # Calculate how often major service items are needed
    major_interval_miles = rules["major_service"]["base_interval_miles"]
    major_cost = rules["major_service"]["base_cost"]
    # How many times per year does major service happen?
    major_services_per_year = annual_mileage / major_interval_miles
    # Cost per year adjusted for engine size and driving style
    major_yearly_cost = (
        major_services_per_year * 
        major_cost * 
        engine_multiplier * 
        driving_multiplier
    )
    major_monthly = major_yearly_cost / 12
    
    # Sum all monthly costs to get the total monthly maintenance reserve
    total_monthly_cost = service_monthly + tyre_monthly + brake_monthly + major_monthly
    
    # Return rounded to 2 decimal places (pence level)
    return round(total_monthly_cost, 2)