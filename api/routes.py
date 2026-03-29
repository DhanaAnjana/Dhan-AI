from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

from agents.state import get_initial_state
from agents.graph import app_graph
from agents.fortune_teller import run_monte_carlo
from config import groq_client
import chromadb, os

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

    # ── Infer monthly income from actual credit transactions ───────────────
    # This ensures the FIRE number reflects each user's real data, not defaults.
    clean_txns = state.get("clean_transactions", [])
    if clean_txns:
        credits = [t["amount"] for t in clean_txns if t.get("type") == "credit"]
        if credits:
            import statistics
            # Use median credit per month as a proxy for regular income
            inferred_income = statistics.median(credits)
            existing_params = state.get("what_if_params") or {}
            if not existing_params.get("monthly_income"):
                state["what_if_params"] = {
                    **existing_params,
                    "monthly_income": inferred_income,
                    "monthly_sip": max(0, inferred_income * 0.15),  # default 15% savings rate
                    "current_corpus": existing_params.get("current_corpus", 200000.0),
                    "age": existing_params.get("age", 28),
                }
    
    # Thread the state context through all Agent Nodes sequentially
    final_state = app_graph.invoke(state)
    
    # Strip and send back actionable UI components — include full_state for frontend to cache
    return {
        "final_response": final_state.get("final_response", ""),
        "roadmap": final_state.get("roadmap", []),
        "full_state": {
            "user_persona": final_state.get("user_persona", ""),
            "ghost_expenses": final_state.get("ghost_expenses", []),
            "fi_number": final_state.get("fi_number", 0),
            "monte_carlo_success_rate": final_state.get("monte_carlo_success_rate", 0),
            "roadmap": final_state.get("roadmap", []),
        }
    }


class FollowUpRequest(BaseModel):
    user_query: str
    cached_state: Optional[Dict[str, Any]] = None

@router.post("/followup")
async def followup_endpoint(request: FollowUpRequest):
    """
    Lightweight Q&A endpoint for follow-up chat messages.
    Uses the RAG specialist + cached state to answer contextually
    WITHOUT re-running the expensive 4-agent pipeline.
    """
    query = request.user_query
    cached = request.cached_state or {}

    # Build a rich context string from the already-computed state
    persona = cached.get("user_persona", "the user")
    fi_number = cached.get("fi_number", 0)
    success_rate = cached.get("monte_carlo_success_rate", 0)
    ghost_expenses = cached.get("ghost_expenses", [])
    roadmap = cached.get("roadmap", [])

    # Pull relevant docs from ChromaDB
    try:
        store_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_store")
        client = chromadb.PersistentClient(path=store_path)
        collection = client.get_or_create_collection(name="dhan_i_knowledge")
        results = collection.query(query_texts=[query], n_results=3)
        docs = results.get("documents", [[]])[0]
        rag_context = "\n\n".join(docs) if docs else "No specific knowledge found."
    except Exception:
        rag_context = "No specific knowledge found."

    system_prompt = f"""You are Dhan-I, a personal Indian finance coach. You already know this person well:
- Their financial persona: {persona}
- Their FIRE target corpus: Rs.{fi_number:,.0f}
- Monte Carlo success probability: {success_rate:.1f}%
- Ghost expenses identified: {ghost_expenses}
- Their 6-month roadmap: {roadmap}

Relevant financial knowledge:
{rag_context}

Answer the user's question using this context. Be specific, friendly, and use Indian examples.
Keep it concise (3-5 sentences max). Use Rs. for currency. No dollar signs."""

    try:
        completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.4,
            max_tokens=512
        )
        answer = completion.choices[0].message.content.strip()
    except Exception as e:
        answer = f"I'm having a moment! Try again: {str(e)}"

    return {"final_response": answer}

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
