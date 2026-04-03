"""Unit tests for fuel cost estimation engine."""

import pytest
from backend.services.cost_engine import (
    get_engine_band,
    calculate_behaviour_adjustment,
    estimate_monthly_fuel_cost
)


def test_engine_band_petrol():
    """Test engine band classification for petrol vehicles."""
    assert get_engine_band("petrol", 1200) == "0-1400"
    assert get_engine_band("petrol", 1500) == "1400-2000"
    assert get_engine_band("petrol", 2500) == "2000-3000"
    assert get_engine_band("petrol", 4000) == "3000+"


def test_engine_band_hybrid():
    """Test that hybrid vehicles return 'any' band."""
    assert get_engine_band("hybrid", 1000) == "any"
    assert get_engine_band("hybrid", 5000) == "any"


def test_engine_band_invalid():
    """Test that invalid fuel type raises ValueError."""
    with pytest.raises(ValueError):
        get_engine_band("nuclear", 2000)


def test_behaviour_adjustment_calm():
    """Test calm driving reduces fuel costs."""
    calm = calculate_behaviour_adjustment(0, "calm", "low")
    assert calm == 1.0
    brisk = calculate_behaviour_adjustment(0, "brisk", "low")
    assert brisk < calm


def test_behaviour_adjustment_city():
    """Test that city driving increases consumption."""
    highway = calculate_behaviour_adjustment(0, "calm", "low")
    city = calculate_behaviour_adjustment(100, "calm", "low")
    assert city < highway


def test_behaviour_adjustment_short_trips():
    """Test that short trips increase consumption."""
    low = calculate_behaviour_adjustment(0, "calm", "low")
    high = calculate_behaviour_adjustment(0, "calm", "high")
    assert high > low


def test_behaviour_adjustment_invalid():
    """Test invalid parameters raise errors."""
    with pytest.raises(ValueError):
        calculate_behaviour_adjustment(-1, "normal", "low")
    with pytest.raises(ValueError):
        calculate_behaviour_adjustment(101, "normal", "low")


def test_fuel_cost_basic():
    """Test fuel cost is calculated for different fuel types."""
    cost_petrol = estimate_monthly_fuel_cost("petrol", 1600, 10000, 1.50, 0, "normal", "low")
    cost_diesel = estimate_monthly_fuel_cost("diesel", 1600, 10000, 1.40, 0, "normal", "low")
    cost_hybrid = estimate_monthly_fuel_cost("hybrid", 1800, 10000, 1.50, 0, "normal", "low")
    assert all(c > 0 for c in [cost_petrol, cost_diesel, cost_hybrid])


def test_fuel_cost_increases_with_mileage():
    """Test that higher mileage increases fuel cost."""
    low = estimate_monthly_fuel_cost("petrol", 1600, 5000, 1.50, 0, "normal", "low")
    high = estimate_monthly_fuel_cost("petrol", 1600, 20000, 1.50, 0, "normal", "low")
    assert high > low


def test_fuel_cost_increases_with_price():
    """Test that higher fuel price increases cost."""
    cheap = estimate_monthly_fuel_cost("petrol", 1600, 10000, 1.20, 0, "normal", "low")
    expensive = estimate_monthly_fuel_cost("petrol", 1600, 10000, 2.00, 0, "normal", "low")
    assert expensive > cheap


def test_fuel_cost_engine_size_matters():
    """Test that larger engines cost more to fuel."""
    small = estimate_monthly_fuel_cost("petrol", 1000, 10000, 1.50, 0, "normal", "low")
    large = estimate_monthly_fuel_cost("petrol", 3500, 10000, 1.50, 0, "normal", "low")
    assert large > small


def test_fuel_cost_driving_style_matters():
    """Test that brisk driving increases fuel cost."""
    calm = estimate_monthly_fuel_cost("petrol", 1600, 10000, 1.50, 0, "calm", "low")
    brisk = estimate_monthly_fuel_cost("petrol", 1600, 10000, 1.50, 0, "brisk", "low")
    assert brisk > calm


def test_fuel_cost_rounded():
    """Test that fuel cost is rounded to 2 decimal places."""
    cost = estimate_monthly_fuel_cost("petrol", 1600, 10000, 1.50, 0, "normal", "low")
    assert cost == round(cost, 2)
