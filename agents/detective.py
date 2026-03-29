import json
from config import groq_client
from agents.state import AgentState

def detective_agent(state: AgentState) -> dict:
    """
    RAG Agent Node: The Detective
    Analyzes all clean transactions and metrics to assign a behavioral persona,
    categorize expenditures into needs/wants, and find the true ghost expenses.
    """
    clean_transactions = state.get("clean_transactions", [])
    gold_metrics = state.get("gold_metrics", {})
    
    # We will pass these via JSON to the prompt
    tx_json = json.dumps(clean_transactions)
    gold_json = json.dumps(gold_metrics)
    
    prompt = f"""You are a financial detective analyzing a user's bank transactions.
Analyze the following data:
Transactions: {tx_json}
Gold Metrics: {gold_json}

Return ONLY a valid JSON object with NO extra text, comments, or markdown formatting. The JSON must have exactly these 3 keys:
1. "persona": A short string describing their spending behavior (e.g., "The Subscription Collector", "The Impulse Spender").
2. "categorised_transactions": The exact same list of transactions provided, but add a new string field "needs_or_wants" (either "needs" or "wants") to each transaction.
3. "ghost_expenses": A list of strings containing merchant names that appear as recurring small debits.

Valid JSON only:"""

    try:
        if groq_client is None:
            raise Exception("Groq API client is not initialized.")
            
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.1,  # Low temperature to restrict hallucinations and ensure valid JSON
            max_tokens=2048,
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Clean up if the model wraps JSON in markdown blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        data = json.loads(response_text)
        
        # We can update `clean_transactions` with the new fields
        updated_txs = data.get("categorised_transactions", clean_transactions)
        
        return {
            "user_persona": data.get("persona", "The Unknown Spender"),
            "clean_transactions": updated_txs,
            "ghost_expenses": data.get("ghost_expenses", []),
        }
        
    except json.JSONDecodeError:
        # Fall back to the raw string if parsing fails
        return {
            "user_persona": response_text[:200] + "... (Parser Error)",
            "ghost_expenses": [],
        }
    except Exception as e:
        return {
            "user_persona": f"Error: {str(e)}",
            "ghost_expenses": [],
        }
