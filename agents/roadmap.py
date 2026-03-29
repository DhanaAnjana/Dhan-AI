import json
from config import groq_client
from agents.state import AgentState

def roadmap_agent(state: AgentState) -> dict:
    """
    RAG Agent Node: The Roadmap Orchestrator
    Takes the combined knowledge of all other agents and formulates a strict, prioritized
    month-by-month financial implementation roadmap and a final conversational summary.
    """
    user_persona = state.get("user_persona", "")
    ghost_expenses = state.get("ghost_expenses", [])
    fi_number = state.get("fi_number", 0.0)
    success_rate = state.get("monte_carlo_success_rate", 0.0)
    rag_context = state.get("rag_context", "")
    
    # Format inputs for LLM
    prompt = f"""You are the Master Financial Planner orchestrating the user's roadmap.
Based on the following multidimensional user data:
Persona: {user_persona}
Ghost Expenses Identified: {json.dumps(ghost_expenses)}
Financial Independence Target: {fi_number:,.2f}
Probability of hitting FI at 65: {success_rate}%
Specialist RAG Advice: {rag_context}

Generate a realistic month-by-month financial roadmap. 
You MUST strictly follow this priority order for allocation and tasks:
1. Establish an emergency fund of 6 months' expenses.
2. Get term and health insurance.
3. Clear high-interest debt (>12%).
4. Start goal-based SIPs.

Return ONLY a valid JSON object with NO extra text or markdown formatting. The JSON must have exactly two keys:
1. "roadmap": A JSON array where each item has "month" (integer, 1 for month 1, 2 for month 2, etc.), "action" (string), and "amount" (float).
2. "summary": A friendly plain-text summary explaining this overall roadmap to the user directly, written like an expert coach. Highlight their FI success rate and their persona.

Valid JSON only:"""

    try:
        if groq_client is None:
            raise Exception("Groq API client is not initialized.")
            
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You output only strictly formatted JSON objects without conversational padding."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2, 
            max_tokens=2048,
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        data = json.loads(response_text)
        
        return {
            "roadmap": data.get("roadmap", []),
            "final_response": data.get("summary", "I built your actionable roadmap, but I'm unable to summarize it out loud right now.")
        }
        
    except json.JSONDecodeError:
        return {
            "roadmap": [],
            "final_response": f"I had trouble building your formal structural roadmap, but here is my raw thinking:\n{response_text}"
        }
    except Exception as e:
        return {
            "roadmap": [],
            "final_response": f"Oops, an error occurred while calculating your roadmap: {str(e)}"
        }
