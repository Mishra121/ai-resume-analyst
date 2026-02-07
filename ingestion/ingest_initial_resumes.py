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
    def extract_metadata_from_pdf(self, filepath: str):
        email = None
        employeeid = None
        try:
            with pdfplumber.open(filepath) as pdf:
                meta = pdf.metadata
                if meta:
                    email = meta.get("/employee_email")
                    employeeid = meta.get("/employee_id")
        except Exception as e:
            print(f"Failed to read metadata from {filepath}: {e}")

        # Fallback if email missing
        if not email:
            base_name = os.path.basename(filepath).split(".")[0]
            email = f"{base_name}@company.com"

        return email, employeeid

    # Load files
    def load_files(self) -> List[str]:
        patterns = ["*.pdf"] ##keeping pdfs for now
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

        email, employeeid = self.extract_metadata_from_pdf(file_path)


        # Insert employee
        employee = self.db.query(Employee).filter(Employee.email == email).first()
        if not employee:
            employee = Employee(
                name=employee_name,
                email=email,
                employeeid=employeeid
            )
            self.db.add(employee)
            self.db.commit()
            self.db.refresh(employee)
            print(f"Created new employee: {email}")
        else:
            if employeeid and employee.employeeid is None:
                employee.employeeid = employeeid
                self.db.commit()
                print(f"Updated employeeid for {email}")

            print(f"Employee {email} already exists (ID={employee.id})")

        
        # Insert Resume
        resume = self.db.query(Resume).filter(
            Resume.employee_email == email,
            Resume.file_path == file_path
        ).first()

        if not resume:
            resume = Resume(
                employee_email=email,
                file_path=file_path,
                text_md=text
            )
            self.db.add(resume)
            self.db.commit()
            self.db.refresh(resume)
            print(f"Inserted new resume for {email}")
        else:
            print(f"Resume {file_path} for {email} already exists, updating text and chunks")
            resume = Resume(
                id = resume.id,
                employee_email=email,
                file_path=file_path,
                text_md=text,
            )
            self.db.commit()

        # Delete old chunks
        self.db.query(ResumeChunk).filter(
            ResumeChunk.resume_id == resume.id
        ).delete(synchronize_session=False)
        self.db.commit()
        # Insert chunks
        for chunk_text, embed in zip(chunks, embeddings):
            rc = ResumeChunk(
                resume_id=resume.id,
                chunk_text=chunk_text,
                embedding=embed,
                meta_data= {
                    "source":"Manual uploads"
                }
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
