from typing import TypedDict, List, Dict, Optional, Any
import operator
from typing import Annotated

# Using total=False so that not all keys need to be initialized at once
class AgentState(TypedDict, total=False):
    raw_text: str
    file_type: str
    raw_transactions: List[Dict[str, Any]]
    clean_transactions: List[Dict[str, Any]]
    gold_metrics: Dict[str, Any]
    user_persona: str
    ghost_expenses: List[Dict[str, Any]]
    fi_number: float
    monte_carlo_success_rate: float
    rag_context: str
    roadmap: List[Dict[str, Any]]
    user_query: str
    final_response: str
    what_if_params: Optional[Dict[str, Any]]

def get_initial_state() -> AgentState:
    """
    Returns the initial state with sensible defaults so LangGraph 
    can initialize the state without errors.
    """
    return {
        "raw_text": "",
        "file_type": "",
        "raw_transactions": [],
        "clean_transactions": [],
        "gold_metrics": {},
        "user_persona": "",
        "ghost_expenses": [],
        "fi_number": 0.0,
        "monte_carlo_success_rate": 0.0,
        "rag_context": "",
        "roadmap": [],
        "user_query": "",
        "final_response": "",
        "what_if_params": None,
    }
