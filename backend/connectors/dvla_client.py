# backend/connectors/dvla_client.py

import json
from pathlib import Path
from backend.domain.vehicle import Vehicle


def get_vehicle_from_mock(registration: str) -> Vehicle:
    """
    Look up a vehicle by registration number using mock DVLA data.
    
    This function searches the mock data JSON file for a vehicle with the given
    registration number. If found, it returns a Vehicle object. If not found,
    it raises an error.
    
    In the future, this will call the real DVLA API instead of reading a file.
    
    Args:
        registration: The vehicle registration number (e.g., "AB21ABC")
        
    Returns:
        A Vehicle object containing the vehicle's details.
        
    Raises:
        ValueError: If the registration number is not found in the mock data.
    """
    # Normalize the registration: remove whitespace and convert to uppercase
    # This makes the lookup case-insensitive and handles accidental spaces
    registration_clean = registration.upper().strip()
    
    # Build the path to the mock data file
    # Path(__file__) gives this file's location (dvla_client.py)
    # .parent goes up to backend/connectors/
    # .parent again goes up to backend/
    # Then we navigate to mock_data/dvla_example.json
    mock_data_path = Path(__file__).parent.parent / "mock_data" / "dvla_example.json"
    
    # Read the JSON file
    with open(mock_data_path, "r", encoding="utf-8") as file:
        mock_data = json.load(file)
    
    # check if the registration exists in the mock data
    if registration_clean not in mock_data:
        raise ValueError(f"Vehicle with registration '{registration}' not found in mock data")
    
    # Get the vehicle data from the dictionary
    vehicle_data = mock_data[registration_clean]
    
    # Create and return a Vehicle object
    # The ** operator unpacks the dictionary into keyword arguments for the vehicle constructor
    # Pydantic will validate that the data matches the vehicle model
    return Vehicle(**vehicle_data)