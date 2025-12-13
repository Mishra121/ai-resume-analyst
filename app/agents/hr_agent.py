from app.agents.nodes.calendar import availability_node
from app.agents.nodes.summary import resume_summary_node
from app.agents.nodes.talent_gap import talent_gap_node
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes.intent import classify_intent
from app.agents.nodes.rag import rag_search_node
from app.agents.nodes.answer import generate_answer

graph = StateGraph(AgentState)

graph.add_node("classify_intent", classify_intent)
graph.add_node("rag", rag_search_node)
graph.add_node("generate_answer", generate_answer)
graph.add_node("check_availability", availability_node)
graph.add_node("create_summary", resume_summary_node)
graph.add_node("generate_talent_gap", talent_gap_node)

graph.set_entry_point("classify_intent")

def route_intent(state: AgentState):
    if state["intent"] == "availability_check":
        return "check_availability"
    if state["intent"] == "resume_summary":
        return "create_summary"
    if state["intent"] == "talent_gap_analysis":
        return "generate_talent_gap"
    return "rag"

graph.add_conditional_edges("classify_intent", route_intent)
graph.add_edge("rag", "generate_answer")
graph.add_edge("check_availability", "generate_answer")
graph.add_edge("create_summary", "generate_answer")
graph.add_edge("generate_talent_gap", "generate_answer")
graph.add_edge("generate_answer", END)

hr_agent = graph.compile()

print(hr_agent.get_graph().draw_mermaid())

# TODO: add security, tracing, logging and evaluation