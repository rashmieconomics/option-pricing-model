"""Tests for the option-pricing calculations in project.py."""

import pytest

from project import (
    binomial_convergence,
    binomial_price,
    black_scholes,
    compare_models,
    validate_inputs,
)


def test_black_scholes_call_and_put_prices():
    """Check known Black-Scholes prices for a standard one-year option."""
    call_price = black_scholes(100, 100, 1, 0.05, 0.20, "call")
    put_price = black_scholes(100, 100, 1, 0.05, 0.20, "put")

    assert call_price == pytest.approx(10.4506, abs=0.0001)
    assert put_price == pytest.approx(5.5735, abs=0.0001)


def test_binomial_price_is_close_to_black_scholes():
    """A sufficiently large CRR tree should be close to Black-Scholes."""
    black_scholes_price = black_scholes(100, 100, 1, 0.05, 0.20, "call")
    tree_price = binomial_price(100, 100, 1, 0.05, 0.20, "call", 500)

    assert tree_price == pytest.approx(black_scholes_price, abs=0.01)


def test_compare_models_calculates_differences():
    """Comparison results should contain consistent non-negative differences."""
    comparison = compare_models(100, 100, 1, 0.05, 0.20, "call", 100)

    assert comparison["black_scholes"] == pytest.approx(10.4506, abs=0.0001)
    assert comparison["absolute_difference"] == pytest.approx(
        abs(comparison["black_scholes"] - comparison["binomial"])
    )
    assert comparison["percentage_difference"] > 0


def test_validate_inputs_rejects_invalid_values():
    """Invalid financial inputs should raise helpful ValueError exceptions."""
    with pytest.raises(ValueError):
        validate_inputs(-100, 100, 1, 0.05, 0.20, "call", 100)
    with pytest.raises(ValueError):
        validate_inputs(100, 100, 1, 0.05, 0, "call", 100)
    with pytest.raises(ValueError):
        validate_inputs(100, 100, 1, 0.05, 0.20, "straddle", 100)
    with pytest.raises(ValueError):
        validate_inputs(100, 100, 1, 0.05, 0.20, "call", 0)


def test_binomial_convergence_returns_requested_step_sizes():
    """Convergence analysis should calculate every specified tree size."""
    convergence = binomial_convergence(100, 100, 1, 0.05, 0.20, "call")

    assert convergence["black_scholes"] == pytest.approx(10.4506, abs=0.0001)
    assert [result["steps"] for result in convergence["results"]] == [10, 25, 50, 100, 250, 500]
    assert all(result["binomial"] > 0 for result in convergence["results"])
