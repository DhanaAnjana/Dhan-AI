import functools
import numpy as np
from typing import Dict, Any
from agents.state import AgentState

@functools.lru_cache(maxsize=128)
def run_monte_carlo(annual_expenses: float, current_corpus: float, monthly_sip: float, age: int, retire_age: int) -> Dict[str, Any]:
    """
    Runs a Monte Carlo simulation of 1000 iterations to predict the corpus at retirement.
    Takes Nifty 50 historical mean/std and Indian inflation mean/std into account.
    Cached using lru_cache for instant UI response identical what-if scenarios.
    """
    iterations = 1000
    years_to_retire = max(1, retire_age - age)
    
    # Vectorized arrays for 1000 parallel universe simulations
    corpuses = np.full(iterations, current_corpus, dtype=float)
    expenses = np.full(iterations, annual_expenses, dtype=float)
    
    annual_sip_total = monthly_sip * 12.0
    
    # Nifty 50 historical: Mean 12%, Std 18%
    market_returns = np.random.normal(0.12, 0.18, (years_to_retire, iterations))
    # Indian Inflation: Mean 6.5%, Std 1%
    inflation_rates = np.random.normal(0.065, 0.01, (years_to_retire, iterations))
    
    for year in range(years_to_retire):
        corpuses = corpuses * (1 + market_returns[year, :])
        corpuses += annual_sip_total
        expenses = expenses * (1 + inflation_rates[year, :])
        
    # The FI number is the target corpus required to sustain expenses at a 4% SWR
    fi_numbers = expenses / 0.04
    
    # Count how many of the 1000 simulations successfully hit the target FI number
    successes = np.sum(corpuses >= fi_numbers)
    success_rate = (successes / iterations) * 100.0
    
    return {
        "fi_number": float(np.median(fi_numbers)),
        "success_rate": round(float(success_rate), 1),
        "median_corpus": float(np.median(corpuses)),
        "p10_corpus": float(np.percentile(corpuses, 10)),
        "p90_corpus": float(np.percentile(corpuses, 90))
    }

def fortune_teller_agent(state: AgentState) -> dict:
    """
    LangGraph compatible agent node.
    Extracts data from the AgentState, interprets What-If params, and runs the simulation.
    """
    gold_metrics = state.get("gold_metrics") or {}
    what_if_params = state.get("what_if_params") or {}
    
    # Determine base values
    total_monthly_spend = gold_metrics.get("total_monthly_spend", 40000.0)
    annual_expenses = float(total_monthly_spend * 12)
    
    # We default these inputs gracefully if they come up empty in testing
    current_corpus = float(what_if_params.get("current_corpus", 500000.0))
    age = int(what_if_params.get("age", 30))
    base_sip = float(what_if_params.get("monthly_sip", 15000.0))
    
    # Apply user "What-If" controls
    extra_sip = float(what_if_params.get("extra_sip", 0.0))
    retire_early_years = int(what_if_params.get("retire_early_years", 0))
    
    monthly_sip = base_sip + extra_sip
    retire_age = 65 - retire_early_years
    
    # Ensure cache hits by passing exact primitive types positionally
    results = run_monte_carlo(
        float(annual_expenses),
        float(current_corpus),
        float(monthly_sip),
        int(age),
        int(retire_age)
    )
    
    # Return dict of keys to merge into the overall State schema
    return {
        "fi_number": results["fi_number"],
        "monte_carlo_success_rate": results["success_rate"]
    }
