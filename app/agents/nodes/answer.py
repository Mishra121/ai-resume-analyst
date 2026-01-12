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
        # Convert calendar info dict to natural language string
        calendar_data = state["calendar_info"]
        if isinstance(calendar_data, dict):
            availability = calendar_data.get("availability", {})
            next_7_days = availability.get("next_7_days", {})

            answer_parts = ["Here's the availability information:\n"]
            for time_slot, days in next_7_days.items():
                answer_parts.append(f"• {time_slot}: {', '.join(days)}")

            state["answer"] = "\n".join(answer_parts)
        else:
            state["answer"] = str(calendar_data)
        return state

    # Handle talent gap analysis
    if state.get("talent_gap"):
        talent_gap_data = state["talent_gap"]
        if isinstance(talent_gap_data, dict):
            state["answer"] = f"Talent Gap Analysis:\n\n{talent_gap_data.get('analysis', str(talent_gap_data))}"
        else:
            state["answer"] = str(talent_gap_data)
        return state

    # Handle resume summaries
    if state.get("structured_output"):
        structured = state["structured_output"]
        if isinstance(structured, dict) and "resume_summaries" in structured:
            summaries = structured["resume_summaries"]
            if not summaries:
                state["answer"] = "No resumes found matching your query. Please try a different search or check if resumes have been ingested into the system."
            else:
                answer_parts = ["Resume Summaries:\n"]
                for item in summaries:
                    emp_name = item.get("employee", {}).get("name", "Unknown")
                    summary = item.get("summary", "No summary available")
                    answer_parts.append(f"\n**{emp_name}**\n{summary}\n")
                state["answer"] = "\n".join(answer_parts)
        else:
            state["answer"] = str(structured)
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
