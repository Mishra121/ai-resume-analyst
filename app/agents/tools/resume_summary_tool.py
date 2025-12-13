
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SUMMARY_PROMPT = """
Summarize the following resume focusing on:
- Key skills
- Experience level
- Best-fit roles

Resume:
{text}
"""

def resume_summary_tool(resume_text: str):
    response = llm.invoke(SUMMARY_PROMPT.format(text=resume_text))
    return response.content
