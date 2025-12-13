
from app.agents.state import AgentState
from app.agents.tools.talent_gap_tool import talent_gap_tool

def talent_gap_node(state: AgentState):
    state["talent_gap"] = talent_gap_tool(
        query=state["query"],
        resumes=state["resumes"]
    )
    return state
