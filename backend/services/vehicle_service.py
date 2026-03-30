from backend.domain.vehicle import Vehicle
from backend.connectors.dvla_client import get_vehicle as get_vehicle_from_dvla


def get_vehicle(registration: str) -> Vehicle:
    """
    Get a vehicle by its registration number.
    """
    return get_vehicle_from_dvla(registration)