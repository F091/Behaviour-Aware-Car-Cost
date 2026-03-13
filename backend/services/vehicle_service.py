# backend/services/vehicle_service.py

from backend.domain.vehicle import Vehicle
from backend.connectors.dvla_client import get_vehicle_from_mock


def get_vehicle(registration: str) -> Vehicle:
    """
    Get a vehicle by its registration number.
    
    This service function handles vehicle lookup. It calls the DVLA connector
    to retrieve vehicle data and returns it as a Vehicle object.
    
    Currently this is a simple wrapper around the mock connector, but later
    it will be expanded to include additional business logic like cost calculations
    and maintenance risk assessment.
    
    Args:
        registration: The vehicle registration number (e.g., "AB21ABC")
        
    Returns:
        A Vehicle object with the vehicle's details.
        
    Raises:
        ValueError: If the vehicle registration is not found.
    """
    # Call the DVLA connector to look up the vehicle
    vehicle = get_vehicle_from_mock(registration)
    
    # Return the vehicle
    # If the registration is not found, the ValueError from the connector
    # will be raised automatically and handled by the caller
    return vehicle