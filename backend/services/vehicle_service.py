# backend/services/vehicle_service.py

# Import the Vehicle domain model to define the return type
from backend.domain.vehicle import Vehicle

# Import the DVLA connector function that handles actual vehicle lookups
# This connector manages both real API calls and fallback to mock data
from backend.connectors.dvla_client import get_vehicle as get_vehicle_from_dvla


def get_vehicle(registration: str) -> Vehicle:
    """
    Get a vehicle by its registration number.
    
    This is a service layer function that acts as a wrapper around the DVLA connector.
    It abstracts away the details of where vehicle data comes from (real API or mock data)
    so that the rest of the application doesn't need to know about the connector directly.
    
    The function is simple but important - it provides a single entry point for all
    vehicle lookups across the application.
    
    Args:
        registration: The vehicle's registration number (e.g., "AB21ABC")
        
    Returns:
        A Vehicle object containing the vehicle's details (make, model, year, fuel type, engine size)
        
    Raises:
        ValueError: If the vehicle is not found in either the DVLA API or mock data
    """
    # Call the DVLA connector which handles the actual lookup logic
    # If the DVLA API is unavailable, it automatically falls back to mock data
    return get_vehicle_from_dvla(registration)