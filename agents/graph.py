from langgraph.graph import StateGraph, END
from agents.state import AgentState

# Import node functions representing each expert agent
from agents.detective import detective_agent
from agents.fortune_teller import fortune_teller_agent
from rag.specialist import rag_agent
from agents.roadmap import roadmap_agent

# Initialize the workflow graph defined by the central shared State
workflow = StateGraph(AgentState)

# Add all specialized nodes to the workflow
workflow.add_node("detective", detective_agent)
workflow.add_node("fortune_teller", fortune_teller_agent)
workflow.add_node("rag_specialist", rag_agent)
workflow.add_node("roadmap_orchestrator", roadmap_agent)

# Set the deterministic starting point of the multi-agent orchestration
workflow.set_entry_point("detective")

# Define edges forming the graph's sequential execution pipeline
# The state flows directly down this path
workflow.add_edge("detective", "fortune_teller")
workflow.add_edge("fortune_teller", "rag_specialist")
workflow.add_edge("rag_specialist", "roadmap_orchestrator")
workflow.add_edge("roadmap_orchestrator", END)

# Compile into a finalized, runnable LangChain application
app_graph = workflow.compile()
