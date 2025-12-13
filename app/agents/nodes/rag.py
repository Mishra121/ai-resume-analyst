from app.agents.state import AgentState
from app.agents.tools.resume_search import resume_search_tool
from db.session import get_db

def rag_search_node(state: AgentState):
    db = next(get_db())
    results = resume_search_tool(db, state["query"], top_k=5)

    print("RESULT TYPE:", type(results))
    print("FIRST RESULT:", results[0])
    print("FIRST RESULT DIR:", dir(results[0]))

    state["resumes"] = results
    state["retrieved_chunks"] = [
        r["resume_text"] for r in results if r.get("resume_text")
    ]
    return state
