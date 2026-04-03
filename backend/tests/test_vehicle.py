"""Unit tests for Vehicle domain model."""

import pytest
from pydantic import ValidationError
from backend.domain.vehicle import Vehicle


def test_vehicle_creation():
    """Test creating a valid Vehicle object."""
    vehicle = Vehicle(
        registration="AB21ABC",
        make="Toyota",
        model="Corolla",
        year=2021,
        fuel_type="petrol",
        engine_capacity_cc=1598
    )
    assert vehicle.registration == "AB21ABC"
    assert vehicle.make == "Toyota"
    assert vehicle.year == 2021


def test_vehicle_fuel_types():
    """Test creating vehicles with different fuel types."""
    petrol = Vehicle("AB21ABC", "Toyota", "Corolla", 2021, "petrol", 1598)
    diesel = Vehicle("CD22CDE", "Ford", "Focus", 2022, "diesel", 1497)
    hybrid = Vehicle("EF23EFG", "Toyota", "Prius", 2023, "hybrid", 1798)
    
    assert petrol.fuel_type == "petrol"
    assert diesel.fuel_type == "diesel"
    assert hybrid.fuel_type == "hybrid"


def test_vehicle_missing_fields():
    """Test that missing required fields raise ValidationError."""
    with pytest.raises(ValidationError):
        Vehicle(make="Toyota", model="Corolla", year=2021, fuel_type="petrol", engine_capacity_cc=1598)
    
    with pytest.raises(ValidationError):
        Vehicle(registration="AB21ABC", model="Corolla", year=2021, fuel_type="petrol", engine_capacity_cc=1598)


def test_vehicle_invalid_types():
    """Test that invalid field types raise ValidationError."""
    with pytest.raises(ValidationError):
        Vehicle("AB21ABC", "Toyota", "Corolla", "2021", "petrol", 1598)
    
    with pytest.raises(ValidationError):
        Vehicle("AB21ABC", "Toyota", "Corolla", 2021, "petrol", "1598")


def test_vehicle_equality():
    """Test that identical vehicles are equal."""
    v1 = Vehicle("AB21ABC", "Toyota", "Corolla", 2021, "petrol", 1598)
    v2 = Vehicle("AB21ABC", "Toyota", "Corolla", 2021, "petrol", 1598)
    assert v1 == v2


def test_vehicle_inequality():
    """Test that different vehicles are not equal."""
    v1 = Vehicle("AB21ABC", "Toyota", "Corolla", 2021, "petrol", 1598)
    v2 = Vehicle("CD22CDE", "Ford", "Focus", 2022, "diesel", 1497)
    assert v1 != v2
