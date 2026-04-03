"""Unit tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


def test_health_check():
    """Test health check endpoint returns ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_vehicle_valid():
    """Test retrieving vehicle with valid registration."""
    response = client.get("/vehicle/AB21ABC")
    assert response.status_code == 200
    data = response.json()
    assert "registration" in data
    assert "make" in data
    assert "fuel_type" in data
    assert "engine_capacity_cc" in data


def test_get_vehicle_invalid():
    """Test retrieving vehicle with invalid registration returns 404."""
    response = client.get("/vehicle/INVALID999")
    assert response.status_code == 404


def test_estimate_fuel_cost():
    """Test fuel cost estimation endpoint."""
    response = client.get(
        "/estimate/fuel/AB21ABC",
        params={
            "annual_mileage": 10000,
            "fuel_price_per_litre": 1.50,
            "city_ratio": 50,
            "driving_style": "normal",
            "short_trip_frequency": "low"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "estimated_monthly_fuel_cost" in data
    assert data["estimated_monthly_fuel_cost"] > 0


def test_estimate_fuel_cost_missing_params():
    """Test fuel cost endpoint validates required parameters."""
    response = client.get("/estimate/fuel/AB21ABC", params={"annual_mileage": 10000})
    assert response.status_code == 422  # Validation error


def test_estimate_ownership_cost():
    """Test full ownership cost estimation endpoint."""
    response = client.get(
        "/estimate/ownership/AB21ABC",
        params={
            "annual_mileage": 10000,
            "fuel_price_per_litre": 1.50,
            "city_ratio": 50,
            "driving_style": "normal",
            "short_trip_frequency": "low"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_monthly_running_cost" in data
    assert "maintenance_breakdown" in data
    assert "fuel_explanation" in data
    assert "insight_summary" in data
    assert data["total_monthly_running_cost"] > 0


def test_estimate_ownership_cost_consistency():
    """Test that total cost equals fuel + maintenance."""
    response = client.get(
        "/estimate/ownership/AB21ABC",
        params={
            "annual_mileage": 10000,
            "fuel_price_per_litre": 1.50,
            "city_ratio": 50,
            "driving_style": "normal",
            "short_trip_frequency": "low"
        }
    )
    data = response.json()
    total = data["total_monthly_running_cost"]
    fuel = data["estimated_monthly_fuel_cost"]
    maintenance = data["estimated_monthly_maintenance_cost"]
    assert abs(total - (fuel + maintenance)) < 0.01


def test_estimate_ownership_cost_invalid_registration():
    """Test ownership cost with invalid registration returns 404."""
    response = client.get(
        "/estimate/ownership/INVALID999",
        params={"annual_mileage": 10000, "fuel_price_per_litre": 1.50}
    )
    assert response.status_code == 404
