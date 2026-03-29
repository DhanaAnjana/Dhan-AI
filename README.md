# Dhan-I: Your AI-Powered Cognitive Financial Twin

Dhan-I is an advanced AI-powered Cognitive Financial Twin designed to turn confused Indian savers into confident investors. By analyzing and extracting raw banking telemetry with PaddleOCR, a fleet of LangGraph micro-agents automatically maps a user's unique financial footprint. It detects dangerous "ghost expenses", isolates financial behaviors into a distinct Persona, and generates a concrete, mathematically-backed Execution Roadmap. 

At the core of Dhan-I sits a highly responsive Interactive What-If Simulator running local Monte Carlo probabilistic models overlaid against Nifty-50 historical data and Indian inflation vectors. This interactive gateway allows the user to immediately understand their precise Financial Independence (FIRE) number, dynamically tweaking their SIP investments and retirement timeline to calculate their 10-year probability of absolute financial success. All driven through a clean Next.js architecture orchestrated seamlessly under the hood without complicated accounting jargon.

## Local Development Guide

1. **Clone the Repo:** Git clone the project to your local machine.
2. **Install Requirements:** Install backend dependencies quickly by running `pip install -r requirements.txt`. (Node modules for frontend must be installed via `cd frontend && npm install`).
3. **Set Environment Keys:** Copy the `.env.example` file to `.env` in the root directory and add your real `GROQ_API_KEY`. (Ensure you have a free tier LLM key from console.groq.com).
4. **Seed the Vector Database:** Before starting, run `python -m rag.seed` once. This populates your local ChromaDB allowing the RAG Agent to pull contextual semantic knowledge automatically.
5. **Start the API Backend:** Boot up the FastAPI backend using `uvicorn main:app --reload` and navigate separately to your frontend dir and run `npm run dev`.

## The Demo Flow (Hackathon Judging)

To experience the full capability of Dhan-I, open the application and upload any test bank statement (PDF, PNG, JPG). Once processed, the app will instantly launch into the Chat interface where our LangGraph agent fleet analyzes your timeline and displays your Spending Persona. Navigate into the **Dashboard**, where the AI isolates hidden liabilities showing recurring *Ghost Expenses* paired alongside their staggering 10-year opportunity cost. Finally, scroll to the interactive **What-If FIRE Dashboard**. Observe your precision FI number and Success Rate. Drag the "Invest more per month" slider slightly to the right, and watch the entire Monte Carlo projection recalculate across thousands of iterative simulations instantly visually displaying your new P10-to-P90 corpus spread!

> **⚠️ DEMO CRITICAL NOTE:** The live production deployment operates on Render's free-tier infrastructure. Due to these constraints, the backend will completely "spin down" after 15 minutes of inactivity. For the smoothest live judging experience, ping or navigate to the deployed Render URL manually 1-2 minutes before presenting to wake the service up from cold-sleep. 