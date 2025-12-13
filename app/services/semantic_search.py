from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import text

from langchain_openai import OpenAIEmbeddings

from app.core.constants import EMBED_MODEL


class SemanticSearchService:
    def __init__(self, db: Session):
        self.db = db
        self.embedder = OpenAIEmbeddings(model=EMBED_MODEL)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> List[Dict]:
        # 1️⃣ Generate query embedding
        query_embedding = self.embedder.embed_query(query)

        # 2️⃣ pgvector similarity search
        # Using cosine distance (<=>)
        sql = text("""
            SELECT
                r.id AS resume_id,
                r.file_path,
                r.text_md,
                e.id AS employee_id,
                e.name AS employee_name,
                e.role AS employee_role,
                MIN(rc.embedding <=> (:embedding)::vector) AS score
            FROM resume_chunks rc
            JOIN resumes r ON r.id = rc.resume_id
            JOIN employees e ON e.id = r.employee_id
            GROUP BY r.id, e.id
            ORDER BY score ASC
            LIMIT :top_k;
        """)

        rows = self.db.execute(
            sql,
            {
                "embedding": query_embedding,
                "top_k": top_k,
            },
        ).mappings().all()

        # 3️⃣ Format response
        results = []
        for row in rows:
            results.append({
                "resume_id": row["resume_id"],
                "score": float(row["score"]),
                "employee": {
                    "id": row["employee_id"],
                    "name": row["employee_name"],
                    "role": row["employee_role"],
                },
                "file_path": row["file_path"],
                "resume_text": row["text_md"],
            })

        return results
