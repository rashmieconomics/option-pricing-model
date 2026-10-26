## Demo Video

[Watch the project demonstration](https://youtu.be/Ak_yeVf5_1g)
## Financial Concepts Used

An option gives its holder the right, but not the obligation, to buy or sell an underlying asset at a fixed strike price.

- A **call option** has payoff `max(S - K, 0)` at expiration, where `S` is the final asset price and `K` is the strike price.
- A **put option** has payoff `max(K - S, 0)` at expiration.
- The **spot price** is the current market price of the underlying asset.
- **Volatility** measures the assumed variability of the underlying price.
- The **risk-free rate** is used to discount expected future values back to the present.
- **Time to maturity** is the time, in years, until the option expires.

Both models price European options, meaning the option may only be exercised at expiration.

## Black-Scholes Model

The `black_scholes()` function calculates the theoretical value of a European call or put under the Black-Scholes assumptions. It calculates the quantities `d1` and `d2` using the spot price, strike price, time to maturity, interest rate, and volatility. It then uses a cumulative normal distribution function to calculate the price.

The program implements the cumulative normal distribution with `math.erf`, which is part of the Python standard library. No external statistics or finance library is required. For a call, the formula values the expected upside after discounting the strike price. For a put, it uses the corresponding put formula.

## Cox-Ross-Rubinstein Binomial Model

The `binomial_price()` function implements a basic CRR binomial tree. In each small time step, the underlying asset can move up by a factor `u` or down by a factor `d`. The model calculates a risk-neutral probability, then values the option in two stages:

1. It uses lists and loops to calculate all possible asset prices and option payoffs at maturity.
2. It works backwards through the tree. At each earlier node, the option value is the discounted risk-neutral expected value of the two following nodes.

The function returns the value at time zero. This backward-induction process is a simple numerical method and makes the tree's calculation visible in the source code.

## Model Comparison and Convergence

The `compare_models()` function returns the Black-Scholes price, binomial price, absolute difference, and percentage difference. The program displays the results in a readable terminal format.

The `binomial_convergence()` function calculates binomial prices using 10, 25, 50, 100, 250, and 500 steps and displays them with the Black-Scholes price. The binomial result should generally become closer to the Black-Scholes result as the number of steps grows, although the approach is not necessarily perfectly smooth at every step count. The purpose of the table is to observe numerical approximation rather than assume a result.

## Files

- `project.py` contains the command-line interface and all pricing, validation, comparison, scenario, and display functions.
- `test_project.py` contains automated pytest tests for Black-Scholes pricing, binomial pricing, comparisons, validation, and convergence output.
- `requirements.txt` lists `pytest`, the only external package needed to run the tests.
- `README.md` is this project documentation.

## Design Choices

The project uses a function-based structure so that the financial calculations can be tested without interacting with the menu. `validate_inputs()` raises `ValueError` for invalid values such as non-positive spot prices, strikes, maturities, volatilities, or binomial step counts, and for invalid option types. A non-positive maturity or volatility is rejected because the formulas divide by volatility times the square root of time.

The binomial tree uses ordinary lists and nested loops instead of a specialized library. This is less compact than a professional numerical implementation, but it is more appropriate for learning and makes the backward valuation process easier to explain. The program includes five predefined call-option scenarios: at-the-money, in-the-money, out-of-the-money, high volatility, and near expiration.

## Testing

The test suite checks the core logic instead of menu output. It verifies known Black-Scholes call and put prices, checks that a 500-step binomial price is close to the Black-Scholes price, confirms that model-comparison differences are calculated correctly, verifies that invalid inputs raise exceptions, and checks the convergence result structure.

Install the testing dependency and run the tests with:

```bash
pip install -r requirements.txt
pytest test_project.py -q
```

## How to Run

Use Python 3. Then run:

```bash
python project.py
```

Choose an item from the menu. Options 1 and 2 prompt for option inputs. Option 3 prints the binomial convergence table for the entered option. Option 4 runs all predefined scenarios. Option 5 exits the program.

For example, a standard at-the-money call can use these inputs:

```text
Spot price: 100
Strike price: 100
Time to maturity: 1
Risk-free rate: 0.05
Volatility: 0.20
Option type: call
Number of binomial steps: 100
```

## Limitations

This is an educational implementation with important limitations. Black-Scholes assumes constant volatility and interest rates, continuous trading, a lognormally distributed asset price, and no transaction costs. Real markets do not meet these assumptions exactly. The model also treats volatility as an input rather than estimating it from market data.

The CRR binomial model makes similarly simplified assumptions. Its output is an approximation that depends on the number of steps, and a large number of steps can make the straightforward list-and-loop implementation slower. The program only prices European options; it does not price American options, use live market data, calculate implied volatility, calibrate a volatility surface, or model dividends. A production valuation system would require stronger numerical controls, market-data handling, model governance, and far more extensive testing.


