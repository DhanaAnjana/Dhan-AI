"""
agents/preprocessor.py
A preprocessing node that runs before the Detective agent.
Converts raw_text → silver (clean_transactions) → gold (metrics + ghost expenses).
This populates AgentState with real data so all downstream agents have actual numbers.
"""
from data_pipeline.silver import process_silver
from data_pipeline.bronze import detect_bank
from data_pipeline.gold import compute_gold_metrics
from agents.state import AgentState


def preprocessor_node(state: AgentState) -> dict:
    """
    LangGraph node that runs the Silver + Gold data pipeline deterministically
    before any LLM agents touch the state.
    """
    raw_text = state.get("raw_text", "")

    if not raw_text or len(raw_text.strip()) < 20:
        # Nothing to process — return empty but valid state
        return {
            "clean_transactions": [],
            "gold_metrics": {},
            "ghost_expenses": [],
        }

    # ── Silver Layer: parse raw PDF text into structured transactions ──
    bank_name = detect_bank(raw_text)
    clean_transactions = process_silver(raw_text, bank_name)

    # ── Infer monthly income from credits in the transaction list ──
    credits = [t["amount"] for t in clean_transactions if t.get("type") == "credit"]
    if credits:
        # Use the maximum single credit as the best proxy for salary
        # (avoids small P2P credits like "received from friend" dragging it down)
        monthly_income = max(credits)
    else:
        monthly_income = 40000.0  # sensible Indian default

    # ── Gold Layer: compute all deterministic financial metrics ──
    gold_metrics = compute_gold_metrics(clean_transactions, monthly_income)

    # ── Structured ghost expenses from Gold layer (with opportunity costs) ──
    ghost_expenses_structured = gold_metrics.get("ghost_expenses", [])

    # ── Set what_if_params based on real data ──
    total_monthly_spend = gold_metrics.get("total_monthly_spend", 40000.0)
    existing_params = state.get("what_if_params") or {}
    what_if_params = {
        "monthly_income": monthly_income,
        "monthly_expense": total_monthly_spend,
        # Default SIP = whatever is left after spend (or 10% of income minimum)
        "monthly_sip": max(monthly_income * 0.10, monthly_income - total_monthly_spend),
        "current_corpus": existing_params.get("current_corpus", 200000.0),
        "age": existing_params.get("age", 28),
    }

    return {
        "clean_transactions": clean_transactions,
        "gold_metrics": gold_metrics,
        "ghost_expenses": ghost_expenses_structured,
        "what_if_params": what_if_params,
    }
