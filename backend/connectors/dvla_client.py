# backend/connectors/dvla_client.py

import os
import json
import requests
from pathlib import Path
from backend.domain.vehicle import Vehicle


def get_vehicle_from_mock(registration: str) -> Vehicle:
    """
    Look up a vehicle by registration number using mock data.
    
    Args:
        registration: The vehicle registration number
        
    Returns:
        A Vehicle object from mock data.
        
    Raises:
        ValueError: If the registration is not found in mock data.
    """
    registration_clean = registration.upper().strip()
    
    # Path to mock data file
    mock_data_path = Path(__file__).parent.parent / "mock_data" / "dvla_example.json"
    
    # Read the mock data file
    with open(mock_data_path, "r", encoding="utf-8") as file:
        mock_data = json.load(file)
    
    # Check if registration exists in mock data
    if registration_clean not in mock_data:
        raise ValueError(f"Vehicle with registration '{registration}' not found in mock data")
    
    # Get the vehicle data
    vehicle_data = mock_data[registration_clean]
    
    # Normalize fuel type to lowercase
    if 'fuel_type' in vehicle_data:
        vehicle_data['fuel_type'] = vehicle_data['fuel_type'].lower()
    
    # Return Vehicle object
    return Vehicle(**vehicle_data)


def get_vehicle(registration: str) -> Vehicle:
    """
    Look up a vehicle by registration number using the DVLA API.
    Falls back to mock data if the API fails or returns 404.
    
    This function calls the DVLA Vehicle Enquiry Service to get vehicle details
    for a given registration number. The API key must be set as an environment
    variable: DVLA_API_KEY
    
    If the DVLA API is unavailable or the vehicle is not found, the system
    automatically falls back to mock data.
    
    Args:
        registration: The vehicle registration number (e.g., "AB21ABC")
        
    Returns:
        A Vehicle object containing the vehicle's details.
        
    Raises:
        ValueError: If the vehicle is not found in both DVLA API and mock data.
    """
    # Get the API key from environment variable
    api_key = os.getenv('DVLA_API_KEY')
    if not api_key:
        # If no API key is set, fall back to mock data
        return get_vehicle_from_mock(registration)
    
    # Normalize the registration: remove whitespace and convert to uppercase
    registration_clean = registration.upper().strip()
    
    # DVLA API endpoint
    url = 'https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles'
    
    # Request headers
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Request body
    body = {
        'registrationNumber': registration_clean
    }
    
    # Make the API call
    try:
        response = requests.post(url, json=body, headers=headers, timeout=10)
        
        # Handle 404 - vehicle not found
        if response.status_code == 404:
            return get_vehicle_from_mock(registration)
        
        # Handle other error status codes
        if response.status_code != 200:
            return get_vehicle_from_mock(registration)
        
        # Parse the JSON response
        api_data = response.json()
        
    except Exception:
        # If any error occurs during API call, fall back to mock data
        return get_vehicle_from_mock(registration)
    
    # Map and normalize fuel type
    fuel_type_raw = api_data.get('fuelType', 'petrol').lower()
    if fuel_type_raw in ('electric', 'hybrid'):
        fuel_type = 'hybrid'
    elif fuel_type_raw == 'diesel':
        fuel_type = 'diesel'
    else:
        fuel_type = 'petrol'
    
    # Extract vehicle data from API response
    vehicle_data = {
        'registration': registration_clean,
        'make': api_data.get('make', ''),
        'model': api_data.get('model', ''),
        'year': api_data.get('yearOfManufacture', 0),
        'fuel_type': fuel_type,
        'engine_capacity_cc': api_data.get('engineCapacity', 0)
    }
    
    # Validate that required fields are present
    if not vehicle_data['make'] or not vehicle_data['model']:
        # If API response is incomplete, fall back to mock data
        return get_vehicle_from_mock(registration)
    
    # Create and return a Vehicle object from API data
    return Vehicle(**vehicle_data)