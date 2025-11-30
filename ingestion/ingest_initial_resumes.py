import os
import glob
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from sqlalchemy.orm import Session

from db.session import get_db
from db.models.employee import Employee
from db.models.resume import Resume
from db.models.resume_chunk import ResumeChunk

# --------- CONFIG ---------
SOURCE_DIR = "source_files"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 100
EMBED_MODEL = "text-embedding-3-small"
# --------------------------

# Optional: install these packages in requirements.txt
# pdfplumber==0.9.0
# python-docx==0.8.11

import pdfplumber
import docx


class ResumeIngestionPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.embedder = OpenAIEmbeddings(model=EMBED_MODEL)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )

    # Load files
    def load_files(self) -> List[str]:
        patterns = ["*.pdf", "*.docx", "*.md"]
        files = []
        for p in patterns:
            files.extend(glob.glob(os.path.join(SOURCE_DIR, p)))
        return files

    # Convert file → text
    def file_to_text(self, filepath: str) -> str:
        ext = filepath.split(".")[-1].lower()
        if ext == "md":
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == "pdf":
            text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        elif ext == "docx":
            doc = docx.Document(filepath)
            text = "\n".join([p.text for p in doc.paragraphs])
            return text
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    # Chunk text
    def chunk_text(self, text: str) -> List[str]:
        return self.splitter.split_text(text)

    # Generate embeddings
    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        return self.embedder.embed_documents(chunks)

    # Insert into DB
    def insert_into_db(self, employee_name: str, file_path: str, text: str,
                   chunks: List[str], embeddings: List[List[float]]):
        # Create employee
        employee = Employee(name=employee_name)
        self.db.add(employee)
        self.db.commit()
        self.db.refresh(employee)

        # Create resume with correct column names
        resume = Resume(employee_id=employee.id, file_path=file_path, text_md=text)
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)

        # Insert chunks
        for chunk_text, embed in zip(chunks, embeddings):
            rc = ResumeChunk(
                resume_id=resume.id,
                chunk_text=chunk_text,
                embedding=embed
            )
            self.db.add(rc)

        self.db.commit()

    # Full pipeline
    def run(self):
        files = self.load_files()
        print(f"Found {len(files)} resumes")

        for fpath in files:
            print(f"\n>>> Processing: {fpath}")

            text = self.file_to_text(fpath)
            chunks = self.chunk_text(text)
            embeddings = self.embed_chunks(chunks)

            emp_name = os.path.basename(fpath).split(".")[0]

            self.insert_into_db(emp_name, fpath, text, chunks, embeddings)
            print(f"Inserted {len(chunks)} chunks for {emp_name}")


if __name__ == "__main__":
    db = next(get_db())
    pipeline = ResumeIngestionPipeline(db)
    pipeline.run()
    print("\nIngestion complete!")
