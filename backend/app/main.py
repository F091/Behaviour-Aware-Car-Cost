# backend/app/main.py

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException

# Import the Vehicle model from the domain layer
from domain.vehicle import Vehicle


# Create the FastAPI application instance
# This is the web server that will handle HTTP requests
app = FastAPI(
    title="Car Cost System API",
    description="API for vehicle lookup and cost estimation",
    version="0.1.0"
)


def load_mock_dvla_data():
    """
    Load vehicle data from the mock JSON file.
    
    This function reads the dvla_example.json file and returns it as a dictionary.
    In a real system, this would call the actual DVLA API. For now, we use
    mock data stored in a JSON file.
    
    Returns:
        A dictionary where keys are registration numbers and values are vehicle details.
    """
    # Build the path to the mock data file
    # Path(__file__) gives us the location of this file (main.py)
    # .parent goes up one folder (to backend/app/)
    # .parent again goes up to backend/
    # Then we navigate to mock_data/dvla_example.json
    mock_data_path = Path(__file__).parent.parent / "mock_data" / "dvla_example.json"
    
    # Open and read the JSON file
    with open(mock_data_path, "r") as file:
        data = json.load(file)
    
    return data


# Load the mock data once when the app starts
# We store it in a variable so we don't have to read the file every time someone makes a request
mock_dvla_data = load_mock_dvla_data()


@app.get("/vehicle/{registration}", response_model=Vehicle)
def get_vehicle(registration: str):
    """
    Retrieve vehicle details by registration number.
    
    This endpoint takes a registration number as input, looks it up in the mock data,
    and returns the vehicle details. If the registration is not found, it returns a 404 error.
    
    Args:
        registration: The vehicle registration number (e.g., "AB21ABC")
        
    Returns:
        A Vehicle object with the vehicle's details (make, model, year, fuel_type, etc.)
        
    Raises:
        HTTPException: A 404 error if the registration is not found in the mock data
    """
    # Convert the registration to uppercase for consistent lookup
    # This makes it so "ab21abc" and "AB21ABC" both work
    registration_upper = registration.upper()
    
    # Check if the registration exists in our mock data
    if registration_upper not in mock_dvla_data:
        # If it doesn't exist, raise a 404 error
        raise HTTPException(
            status_code=404,
            detail=f"Vehicle with registration '{registration}' not found"
        )
    
    # Get the vehicle data from the dictionary
    vehicle_data = mock_dvla_data[registration_upper]
    
    # Create and return a Vehicle object from the data
    # Pydantic will automatically validate that the data matches the Vehicle model
    return Vehicle(**vehicle_data)


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


# This allows the app to be run directly with: python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
