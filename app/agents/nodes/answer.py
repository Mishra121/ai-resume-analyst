from langchain_openai import ChatOpenAI
from app.agents.state import AgentState

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

ANSWER_PROMPT = """
You are an HR intelligence agent.

Use the following resume data to answer the query.
Be factual. If unsure, say so.

Query:
{query}

Resume Data:
{context}

Return a structured JSON with:
- answer
- candidates
- actions_suggested
"""

def generate_answer(state: AgentState):

    if state.get("calendar_info"):
        state["answer"] = state["calendar_info"]
        return state

    context = "\n\n".join(state.get("retrieved_chunks", []))

    response = llm.invoke(
        ANSWER_PROMPT.format(
            query=state["query"],
            context=context
        )
    )

    state["answer"] = response.content
    return state
