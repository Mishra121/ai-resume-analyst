
from app.agents.state import AgentState
from app.agents.tools.resume_summary_tool import resume_summary_tool
from app.agents.tools.resume_search import resume_search_tool
from db.session import get_db

def resume_summary_node(state: AgentState):
    # First, search for resumes if not already populated
    if not state.get("resumes"):
        db = next(get_db())
        results = resume_search_tool(db, state["query"], top_k=5)
        state["resumes"] = results

    # Generate summaries for found resumes
    summaries = []
    for r in state["resumes"]:
        summaries.append({
            "employee": r["employee"],
            "summary": resume_summary_tool(r["resume_text"])
        })

    state["structured_output"] = {"resume_summaries": summaries}
    return state
