
from app.agents.state import AgentState
from app.agents.tools.resume_summary_tool import resume_summary_tool

def resume_summary_node(state: AgentState):
    summaries = []
    for r in state["resumes"]:
        summaries.append({
            "employee": r["employee"],
            "summary": resume_summary_tool(r["resume_text"])
        })

    state["structured_output"] = {"resume_summaries": summaries}
    return state
