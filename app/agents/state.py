from typing import Dict, List, Optional, TypedDict, Any

class AgentState(TypedDict):
    query: str
    intent: str
    retrieved_chunks: List[str]
    resumes: List[dict]
    calendar_info: Optional[Dict[str, Any]]
    talent_gap: Optional[Dict[str, Any]]

    answer: Optional[str]
    structured_output: Optional[dict]
