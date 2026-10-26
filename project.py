"""Price European options with Black-Scholes and a CRR binomial tree.

This is an educational command-line project. It deliberately uses only the
Python standard library and makes the binomial tree visible through lists and
loops rather than through a finance library.
"""

from math import erf, exp, log, sqrt


SCENARIOS = {
    "At-the-Money": (100, 100, 1, 0.05, 0.20, "call", 100),
    "In-the-Money": (120, 100, 1, 0.05, 0.20, "call", 100),
    "Out-of-the-Money": (80, 100, 1, 0.05, 0.20, "call", 100),
    "High Volatility": (100, 100, 1, 0.05, 0.50, "call", 100),
    "Near Expiration": (100, 100, 0.05, 0.05, 0.20, "call", 100),
}


def main():
    """Run the menu-driven command-line interface."""
    while True:
        print("\n========================================")
        print("   OPTION PRICING & MODEL COMPARISON")
        print("========================================")
        print("1. Price an option")
        print("2. Compare Black-Scholes and Binomial")
        print("3. Study Binomial Convergence")
        print("4. Run Example Scenarios")
        print("5. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "5":
            print("Goodbye.")
            break

        if choice not in {"1", "2", "3", "4"}:
            print("Please enter a number from 1 to 5.")
            continue

        if choice == "4":
            run_scenarios()
            continue

        try:
            inputs = get_option_inputs()
            spot, strike, maturity, rate, volatility, option_type, steps = inputs

            if choice == "1":
                black_scholes_price = black_scholes(
                    spot,
                    strike,
                    maturity,
                    rate,
                    volatility,
                    option_type,
                )

                tree_price = binomial_price(*inputs)

                print(f"\nBlack-Scholes price: ${black_scholes_price:.4f}")
                print(f"Binomial price:      ${tree_price:.4f}")

            elif choice == "2":
                comparison = compare_models(*inputs)
                display_comparison(comparison)

            else:
                convergence = binomial_convergence(
                    spot,
                    strike,
                    maturity,
                    rate,
                    volatility,
                    option_type,
                )
                display_convergence(convergence)

        except ValueError as error:
            print(f"Input error: {error}")


def validate_inputs(
    spot,
    strike,
    maturity,
    rate,
    volatility,
    option_type,
    steps=None,
):
    """Validate option inputs and raise ValueError for invalid values."""

    numeric_values = {
        "spot price": spot,
        "strike price": strike,
        "time to maturity": maturity,
        "risk-free rate": rate,
        "volatility": volatility,
    }

    for name, value in numeric_values.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{name.capitalize()} must be a number.")

    if spot <= 0:
        raise ValueError("Spot price must be greater than zero.")

    if strike <= 0:
        raise ValueError("Strike price must be greater than zero.")

    if maturity <= 0:
        raise ValueError("Time to maturity must be greater than zero.")

    if volatility <= 0:
        raise ValueError("Volatility must be greater than zero.")

    if not isinstance(option_type, str):
        raise ValueError("Option type must be 'call' or 'put'.")

    if option_type.lower() not in {"call", "put"}:
        raise ValueError("Option type must be 'call' or 'put'.")

    if steps is not None:
        if not isinstance(steps, int) or isinstance(steps, bool):
            raise ValueError("Number of binomial steps must be an integer.")

        if steps <= 0:
            raise ValueError(
                "Number of binomial steps must be greater than zero."
            )


def normal_cdf(value):
    """Return the standard normal cumulative probability."""

    return 0.5 * (1 + erf(value / sqrt(2)))


def black_scholes(
    spot,
    strike,
    maturity,
    rate,
    volatility,
    option_type,
):
    """Return the Black-Scholes price of a European call or put option."""

    validate_inputs(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        option_type,
    )

    option_type = option_type.lower()

    d1 = (
        log(spot / strike)
        + (rate + volatility**2 / 2) * maturity
    ) / (volatility * sqrt(maturity))

    d2 = d1 - volatility * sqrt(maturity)

    discounted_strike = strike * exp(-rate * maturity)

    if option_type == "call":
        return (
            spot * normal_cdf(d1)
            - discounted_strike * normal_cdf(d2)
        )

    return (
        discounted_strike * normal_cdf(-d2)
        - spot * normal_cdf(-d1)
    )


def binomial_price(
    spot,
    strike,
    maturity,
    rate,
    volatility,
    option_type,
    steps,
):
    """Return a European option price using a CRR binomial tree."""

    validate_inputs(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        option_type,
        steps,
    )

    option_type = option_type.lower()

    time_step = maturity / steps

    up = exp(volatility * sqrt(time_step))
    down = 1 / up

    growth = exp(rate * time_step)

    probability = (growth - down) / (up - down)

    if not 0 <= probability <= 1:
        raise ValueError(
            "Inputs produce an invalid risk-neutral probability."
        )

    # Calculate option payoffs at expiration.
    option_values = []

    for up_moves in range(steps + 1):
        final_spot = (
            spot
            * (up ** up_moves)
            * (down ** (steps - up_moves))
        )

        if option_type == "call":
            payoff = max(final_spot - strike, 0)
        else:
            payoff = max(strike - final_spot, 0)

        option_values.append(payoff)

    # Work backward through the tree.
    discount = exp(-rate * time_step)

    for level in range(steps, 0, -1):
        next_values = []

        for node in range(level):
            expected_value = (
                probability * option_values[node + 1]
                + (1 - probability) * option_values[node]
            )

            next_values.append(discount * expected_value)

        option_values = next_values

    return option_values[0]


def compare_models(
    spot,
    strike,
    maturity,
    rate,
    volatility,
    option_type,
    steps,
):
    """Compare Black-Scholes and binomial model prices."""

    black_scholes_price = black_scholes(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        option_type,
    )

    tree_price = binomial_price(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        option_type,
        steps,
    )

    absolute_difference = abs(
        black_scholes_price - tree_price
    )

    if black_scholes_price != 0:
        percentage_difference = (
            absolute_difference
            / black_scholes_price
            * 100
        )
    else:
        percentage_difference = 0.0

    return {
        "black_scholes": black_scholes_price,
        "binomial": tree_price,
        "absolute_difference": absolute_difference,
        "percentage_difference": percentage_difference,
    }


def binomial_convergence(
    spot,
    strike,
    maturity,
    rate,
    volatility,
    option_type,
):
    """Calculate binomial prices for increasing tree sizes."""

    validate_inputs(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        option_type,
    )

    black_scholes_price = black_scholes(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        option_type,
    )

    results = []

    for steps in [10, 25, 50, 100, 250, 500]:
        tree_price = binomial_price(
            spot,
            strike,
            maturity,
            rate,
            volatility,
            option_type,
            steps,
        )

        results.append(
            {
                "steps": steps,
                "binomial": tree_price,
            }
        )

    return {
        "black_scholes": black_scholes_price,
        "results": results,
    }


def get_option_inputs():
    """Prompt for and validate option input values."""

    spot = float(input("Spot price: "))
    strike = float(input("Strike price: "))
    maturity = float(input("Time to maturity (years): "))
    rate = float(
        input("Risk-free rate (for example, 0.05): ")
    )
    volatility = float(
        input("Volatility (for example, 0.20): ")
    )
    option_type = input(
        "Option type (call/put): "
    ).strip().lower()

    steps = int(
        input("Number of binomial steps: ")
    )

    validate_inputs(
        spot,
        strike,
        maturity,
        rate,
        volatility,
        option_type,
        steps,
    )

    return (
        spot,
        strike,
        maturity,
        rate,
        volatility,
        option_type,
        steps,
    )


def display_comparison(comparison):
    """Print model comparison results."""

    print("\nMODEL COMPARISON")
    print("-" * 50)

    print(
        f"Black-Scholes Price  : "
        f"${comparison['black_scholes']:.4f}"
    )

    print(
        f"Binomial Price       : "
        f"${comparison['binomial']:.4f}"
    )

    print(
        f"Absolute Difference  : "
        f"${comparison['absolute_difference']:.4f}"
    )

    print(
        f"Percentage Difference: "
        f"{comparison['percentage_difference']:.2f}%"
    )


def display_convergence(convergence):
    """Print the binomial convergence table."""

    print(
        f"\nBlack-Scholes Price: "
        f"${convergence['black_scholes']:.4f}"
    )

    print("Steps       Binomial Price")
    print("-" * 32)

    for result in convergence["results"]:
        print(
            f"{result['steps']:<11} "
            f"${result['binomial']:.4f}"
        )


def run_scenarios():
    """Calculate and display predefined market scenarios."""

    for name, inputs in SCENARIOS.items():
        print(f"\nScenario: {name}")

        comparison = compare_models(*inputs)

        display_comparison(comparison)


if __name__ == "__main__":
    main()
