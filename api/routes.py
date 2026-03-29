from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

from agents.state import get_initial_state
from agents.graph import app_graph
from agents.fortune_teller import run_monte_carlo

router = APIRouter()

class ChatRequest(BaseModel):
    user_query: str
    current_state: Optional[Dict[str, Any]] = None

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Core entry point for Dhan-I. Takes the user's natural language query and context,
    channels it through the full pipeline (Detective -> Fortune Teller -> RAG -> Roadmap).
    """
    # Fetch safe defaults via factory dict
    state = get_initial_state()
    
    # Merge any frontend inputs into main state
    if request.current_state:
        state.update(request.current_state)
        
    state["user_query"] = request.user_query
    
    # Thread the state context through all Agent Nodes sequentially
    final_state = app_graph.invoke(state)
    
    # Strip and send back actionable UI components
    return {
        "final_response": final_state.get("final_response", ""),
        "roadmap": final_state.get("roadmap", [])
    }

@router.get("/calculate")
async def calculate_endpoint(
    monthly_income: float,
    monthly_expense: float,
    current_corpus: float,
    age: int,
    extra_sip: float = 0.0,
    retire_early_years: int = 0
):
    """
    Powers fast interactive visual sliders for Financial Independence.
    Uses lru_cache under the hood to completely bypass processing time on identical hits.
    """
    annual_expenses = float(monthly_expense * 12.0)
    total_monthly_sip = float(max(0.0, monthly_income - monthly_expense) + extra_sip)
    retire_age = int(65 - retire_early_years)
    
    results = run_monte_carlo(
        annual_expenses,
        float(current_corpus),
        total_monthly_sip,
        int(age),
        retire_age
    )
    
    return results

@router.get("/health")
def health_endpoint():
    """
    Simple health check for Docker/Kubernetes or frontend sanity checks.
    """
    return {"status": "ok"}
