# backend/domain/vehicle.py

from pydantic import BaseModel
from typing import Optional


class Vehicle(BaseModel):
    """
    Represents a vehicle in the system.
    
    This is just a data container. It holds basic information about a vehicle
    retrieved from DVLA mock data or API. No logic, no rules—just the facts
    about the vehicle itself.
    """
    registration: str  # e.g. "AB21ABC"
    make: str          # e.g. "Ford"
    model: str         # e.g. "Focus"
    year: int          # e.g. 2021
    fuel_type: str     # One of: "Petrol", "Diesel", "Hybrid"