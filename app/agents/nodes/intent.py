from langchain_openai import ChatOpenAI
from app.agents.state import AgentState

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

INTENT_PROMPT = """
Classify the user query into one of the following intents:
- resume_search
- resume_summary
- availability_check
- general_hr_query
- talent_gap_analysis

Return only the intent string.
Query: {query}
"""

def classify_intent(state: AgentState):
    response = llm.invoke(INTENT_PROMPT.format(query=state["query"]))
    print('intent-----', response.content)
    state["intent"] = response.content.strip()
    return state
