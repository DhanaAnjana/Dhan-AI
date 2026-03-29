import os
import chromadb
from config import groq_client
from agents.state import AgentState

def rag_agent(state: AgentState) -> dict:
    """
    RAG Agent Node:
    Takes a user_query, searches local ChromaDB, formats the context, and
    prompts the Groq LLM to respond using WhatsApp-style vernacular.
    Saves the final response back into rag_context.
    """
    user_query = state.get("user_query", "").strip()
    
    if not user_query:
        # Failsafe if the state lacks a query
        return {"rag_context": "Hey! It looks like you didn't ask a question. How can I help you today? \U0001f60a"}
        
    store_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_store")
    client = chromadb.PersistentClient(path=store_path)
    collection = client.get_or_create_collection(name="dhan_i_knowledge")
    
    try:
        results = collection.query(
            query_texts=[user_query],
            n_results=3
        )
        retrieved_docs = results.get("documents", [[]])[0]
    except Exception as e:
        print(f"ChromaDB Query Error: {e}")
        retrieved_docs = []
        
    if not retrieved_docs:
        context_string = "Sorry, no relevant information could be retrieved."
    else:
        context_string = "\n\n".join(retrieved_docs)
        
    system_prompt = f"""You are a personal finance assistant for the app Dhan-I. 
Your primary goal is to answer the user's question USING ONLY the provided context. 
If the context doesn't contain the answer, warmly say you don't know based on the current knowledge.

RULES:
- Answer ONLY using the provided context.
- Use simple, friendly WhatsApp-style language (short sentences, simple words, emojis).
- Completely avoid heavy financial jargon. Make it sound like a friend texting you.
- Always conclude with a very specific, actionable answer or next step.

CONTEXT:
{context_string}"""

    try:
        if groq_client is None:
            raise Exception("Groq API client is not initialized.")
            
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_query,
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=1024
        )
        
        response = chat_completion.choices[0].message.content
        
    except Exception as e:
        response = f"Oops! I faced a technical glitch while trying to find an answer for you: {str(e)} 🛠️"
        
    return {
        "rag_context": response.strip()
    }
