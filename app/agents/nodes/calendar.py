
from app.agents.state import AgentState
from app.agents.tools.calendar_tool import calendar_availability_tool

def availability_node(state: AgentState):
    employee_ids = [r["employee"]["id"] for r in state["resumes"] if r.get("employee")]
    state["calendar_info"] = calendar_availability_tool(employee_ids)
    return state
