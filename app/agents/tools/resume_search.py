from sqlalchemy.orm import Session
from app.services.semantic_search import SemanticSearchService

def resume_search_tool(
    db: Session,
    query: str,
    top_k: int = 5
):
    service = SemanticSearchService(db)
    return service.search(query=query, top_k=top_k)
