from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.session import get_db
from app.services.semantic_search import SemanticSearchService
from app.agents.hr_agent import hr_agent

router = APIRouter(prefix="/search", tags=["Search"])


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 5

class RAGAgentRequest(BaseModel):
    query: str


@router.post("/semantic")
def semantic_search(
    payload: SemanticSearchRequest,
    db: Session = Depends(get_db),
):
    service = SemanticSearchService(db)

    results = service.search(
        query=payload.query,
        top_k=payload.top_k,
    )

    return {
        "query": payload.query,
        "matches": results,
        "count": len(results),
    }

@router.post("/rag-agent")
def rag_agent_endpoint(req: RAGAgentRequest):
    state = {
        "query": req.query,
        "intent": "",
        "retrieved_chunks": [],
        "resumes": [],
        "calendar_info": None,
        "answer": None,
        "structured_output": None,
    }

    result = hr_agent.invoke(state)
    return {
        "answer": result["answer"]
    }
