"""Unit tests for maintenance cost estimation engine."""

import pytest
from backend.services.maintenance_engine import (
    get_engine_band,
    estimate_monthly_maintenance_cost
)


def test_engine_band_maintenance():
    """Test engine band classification for maintenance."""
    assert get_engine_band(1000) == "0-1400"
    assert get_engine_band(1600) == "1400-2000"
    assert get_engine_band(2500) == "2000-3000"
    assert get_engine_band(4000) == "3000+"


def test_maintenance_cost_basic():
    """Test maintenance cost is positive for valid inputs."""
    cost = estimate_monthly_maintenance_cost(1600, 10000, 50, "normal", "low")
    assert cost > 0


def test_maintenance_cost_increases_with_mileage():
    """Test that higher mileage increases maintenance cost."""
    low = estimate_monthly_maintenance_cost(2000, 5000, 0, "calm", "low")
    high = estimate_monthly_maintenance_cost(2000, 20000, 0, "calm", "low")
    assert high > low


def test_maintenance_cost_engine_size():
    """Test that larger engines cost more to maintain."""
    small = estimate_monthly_maintenance_cost(1000, 10000, 0, "normal", "low")
    large = estimate_monthly_maintenance_cost(3500, 10000, 0, "normal", "low")
    assert large > small


def test_maintenance_cost_driving_style():
    """Test that brisk driving increases maintenance cost."""
    calm = estimate_monthly_maintenance_cost(2000, 10000, 0, "calm", "low")
    brisk = estimate_monthly_maintenance_cost(2000, 10000, 0, "brisk", "low")
    assert brisk > calm


def test_maintenance_cost_city_driving():
    """Test that city driving increases maintenance (brake wear)."""
    highway = estimate_monthly_maintenance_cost(2000, 10000, 0, "normal", "low")
    city = estimate_monthly_maintenance_cost(2000, 10000, 100, "normal", "low")
    assert city > highway


def test_maintenance_cost_short_trips():
    """Test that frequent short trips increase maintenance cost."""
    low = estimate_monthly_maintenance_cost(2000, 10000, 0, "normal", "low")
    high = estimate_monthly_maintenance_cost(2000, 10000, 0, "normal", "high")
    assert high > low


def test_maintenance_cost_rounded():
    """Test that maintenance cost is rounded to 2 decimal places."""
    cost = estimate_monthly_maintenance_cost(2000, 10000, 50, "normal", "low")
    assert cost == round(cost, 2)
