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
    prompt = f"""You are a concise, expert Indian financial planner.

User Profile:
- Persona: {user_persona}
- Ghost Expenses (recurring small debits to cut): {json.dumps(ghost_expenses)}
- Financial Independence Target Corpus: Rs.{fi_number:,.0f}
- Current Monte Carlo Success Probability: {success_rate:.1f}%
- Expert Advice Context: {rag_context[:500]}

Create a practical 6-month action roadmap. Follow this strict priority:
Month 1-2: Emergency Fund (6x monthly expenses)
Month 3: Insurance (term + health)
Month 4-5: Eliminate high-interest debt (above 12%)
Month 6: Begin SIP investments

RULES:
- The "roadmap" array MUST have EXACTLY 6 items (month 1 through 6).
- Each "amount" is a realistic monthly INR figure (not yearly, not cumulative).
- The "summary" is 2-3 sentences max, casual coach tone, mentions persona and success rate.
- Use ONLY Indian Rupees (Rs.). No dollar signs.

Return ONLY this exact JSON structure, no markdown, no extra text:
{{"roadmap": [{{"month": 1, "action": "...", "amount": 15000}}, ...6 items total], "summary": "..."}}"""

    try:
        if groq_client is None:
            raise Exception("Groq API client is not initialized.")
            
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You output only strictly formatted JSON objects without conversational padding."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=1024,
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
        # Don't dump raw JSON to the user — show a clean error and let them retry
        return {
            "roadmap": [],
            "final_response": "I assembled your financial roadmap but ran into a formatting hiccup. Head to the Dashboard to see your FIRE number and ghost expenses — or try asking me a specific question like 'What should I do first?'"
        }
    except Exception as e:
        return {
            "roadmap": [],
            "final_response": f"Oops, an error occurred while calculating your roadmap: {str(e)}"
        }
