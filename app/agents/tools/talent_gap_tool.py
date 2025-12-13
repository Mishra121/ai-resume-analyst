
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

GAP_PROMPT = """
You are an HR strategist.

Given the resumes and the role requirement below, identify:
- Missing skills
- Weak areas
- Hiring recommendations

Role Requirement:
{query}

Resumes:
{context}
"""

def talent_gap_tool(query: str, resumes: list):
    context = "\n\n".join([r["resume_text"] for r in resumes])
    response = llm.invoke(GAP_PROMPT.format(query=query, context=context))

    return {
        "analysis": response.content,
        "recommendation": "Consider hiring or upskilling"
    }
