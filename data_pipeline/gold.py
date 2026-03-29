import pandas as pd
import numpy as np
from typing import List, Dict, Any

def detect_ghost_expenses(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Finds small recurring subscriptions or 'ghost expenses'.
    A ghost expense is defined as a debit under 1000 rupees seen in 3 or more distinct months.
    Returns the merchant, avg amount, months seen, and the 10-year opportunity cost
    if invested at 12% annually.
    """
    if df.empty:
        return []
        
    # Filter for debits under 1000
    debits = df[(df['type'] == 'debit') & (df['amount'] < 1000)].copy()
    
    if debits.empty:
        return []
        
    # Group by merchant to find recurrence
    grouped = debits.groupby('merchant').agg(
        months_seen=('month_year', 'nunique'),
        average_amount=('amount', 'mean')
    ).reset_index()
    
    # Filter for merchants seen in >= 3 distinct months
    ghosts = grouped[grouped['months_seen'] >= 3].copy()
    
    if ghosts.empty:
        return []
        
    # Calculate 10-Year Opportunity Cost (Future Value of Annuity)
    # PMT = Monthly amount (average_amount)
    # r = Monthly interest rate (12% / 12 = 0.01)
    # n = Number of months (10 years * 12 = 120)
    # FV = PMT * (((1 + r)^n - 1) / r)
    r = 0.01
    n = 120
    ghosts['opportunity_cost_10yr'] = ghosts['average_amount'] * (((1 + r)**n - 1) / r)
    
    # Sort by opportunity cost descending
    ghosts = ghosts.sort_values(by="opportunity_cost_10yr", ascending=False)
    
    result = []
    for _, row in ghosts.iterrows():
        result.append({
            "merchant": str(row['merchant']),
            "average_amount": float(round(row['average_amount'], 2)),
            "months_seen": int(row['months_seen']),
            "opportunity_cost_10yr": float(round(row['opportunity_cost_10yr'], 2))
        })
        
    return result

def compute_gold_metrics(clean_transactions: List[Dict[str, Any]], monthly_income: float) -> Dict[str, Any]:
    """
    Computes key financial metrics deterministically.
    Takes the silver layer clean_transactions and user's stated monthly_income.
    """
    if not clean_transactions:
        return {
            "total_monthly_spend": 0.0,
            "savings_rate": 0.0,
            "lifestyle_creep_index": 0.0,
            "top_categories": {},
            "ghost_expenses": []
        }
        
    # Convert list of dicts to a pandas DataFrame
    df = pd.DataFrame(clean_transactions)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['month_year'] = df['date'].dt.to_period('M')
    
    # Base filtering
    debits = df[df['type'] == 'debit'].copy()
    
    if debits.empty:
        return {
            "total_monthly_spend": 0.0,
            "savings_rate": 1.0 if monthly_income > 0 else 0.0,
            "lifestyle_creep_index": 0.0,
            "top_categories": {},
            "ghost_expenses": []
        }
        
    # 1. Total Monthly Spend (Average over all active months)
    monthly_spends = debits.groupby('month_year')['amount'].sum()
    total_monthly_spend = float(monthly_spends.mean()) if not monthly_spends.empty else 20000.0
    
    # Sanity floor for demo: minimum 10k monthly spend
    total_monthly_spend = float(max(10000.0, total_monthly_spend))
    
    # 2. Savings Rate
    # Calculated as: (Income - Average Monthly Spend) / Income
    if monthly_income > 0:
        savings_rate = (monthly_income - total_monthly_spend) / monthly_income
    else:
        savings_rate = 0.0
        
    # 3. Lifestyle Creep Index
    # Month-on-month percentage change in spend, averaged
    lifestyle_creep_index = 0.0
    if len(monthly_spends) > 1:
        # Sort by chronological time explicitly
        monthly_spends = monthly_spends.sort_index()
        pct_change = monthly_spends.pct_change().dropna()
        # Convert to a whole number percentage (e.g., 5.5 = 5.5% increase)
        lifestyle_creep_index = float(pct_change.mean() * 100)
        
    # 4. Top Categories
    # Standardizing "merchant" as the proxy for category in the deterministic layer
    # LLM can further sub-categorize later if needed
    top_merchants = debits.groupby('merchant')['amount'].sum().sort_values(ascending=False).head(15)
    
    # Convert mapping to native float types for JSON compatibility
    top_categories = {str(k): float(round(v, 2)) for k, v in top_merchants.items()}
    
    # 5. Ghost Expenses Detection
    ghost_expenses_list = detect_ghost_expenses(df)
    
    return {
        "total_monthly_spend": float(round(total_monthly_spend, 2)),
        "savings_rate": float(round(savings_rate, 4)),
        "lifestyle_creep_index": float(round(lifestyle_creep_index, 2)),
        "top_categories": top_categories,
        "ghost_expenses": ghost_expenses_list
    }
