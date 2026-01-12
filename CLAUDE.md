# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered resume analysis and matching system built with FastAPI, LangGraph, and PostgreSQL with pgvector. The system uses a multi-node agent architecture to handle HR queries through intent classification and specialized processing nodes.

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11
- OpenAI API key (for embeddings and LLM)

### Initial Setup

1. **Environment Configuration**
   - Copy `.env.example` to `.env` and configure:
     - `OPENAI_API_KEY`
     - PostgreSQL credentials (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`)
     - `DATABASE_URL`

2. **Build and Start Services**
   ```bash
   docker compose build
   docker compose up -d
   ```

3. **Database Setup**
   ```bash
   # Access the database container
   docker compose exec db psql -U postgres -d resumedb

   # Enable pgvector extension (required for embeddings)
   CREATE EXTENSION IF NOT EXISTS vector;
   \q
   ```

4. **Run Database Migrations**
   ```bash
   docker compose exec api bash
   alembic upgrade head
   ```

5. **Ingest Initial Resume Data**
   ```bash
   docker compose exec api python -m ingestion.ingest_initial_resumes
   ```
   - This processes all files in `source_files/` (PDF, DOCX, MD)
   - Extracts text, chunks it, generates embeddings, and stores in database

### Running the Application

```bash
# Start all services
docker compose up

# Access services:
# - Chainlit Chat UI: http://localhost:8001
# - FastAPI Backend: http://localhost:8000
# - API docs: http://localhost:8000/docs
```

**Services:**
- `api` - FastAPI backend with RAG agent
- `chainlit` - Chat UI frontend (communicates with API via HTTP)
- `db` - PostgreSQL with pgvector extension

### Development Commands

```bash
# Access API container shell
docker compose exec api bash

# Run ingestion pipeline
docker compose exec api python -m ingestion.ingest_initial_resumes

# Create new migration
docker compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker compose exec api alembic upgrade head

# Rollback migration
docker compose exec api alembic downgrade -1

# View Chainlit logs
docker compose logs chainlit -f

# Rebuild Chainlit service only
docker compose build chainlit

# Restart Chainlit service
docker compose restart chainlit
```

## Architecture

### Multi-Node Agent System (LangGraph)

The core of the application is a stateful agent graph (`app/agents/hr_agent.py`) that routes queries through specialized nodes based on intent classification.

**Agent Flow:**
1. **Entry Point**: `classify_intent` node determines query type
2. **Conditional Routing**: Routes to one of four specialized nodes:
   - `rag` - Semantic search + context generation for general queries
   - `check_availability` - Calendar/scheduling queries (mock data)
   - `create_summary` - Resume summarization
   - `generate_talent_gap` - Talent gap analysis
3. **Answer Generation**: All paths converge at `generate_answer` node
4. **End**: Returns structured output with answer

**State Management** (`app/agents/state.py`):
- `AgentState` TypedDict tracks data flow through nodes
- Key fields: `query`, `intent`, `retrieved_chunks`, `resumes`, `calendar_info`, `talent_gap`, `answer`, `structured_output`

### Database Schema

**Core Models** (defined in `db/models/`):
- `Employee` - Employee/candidate records
- `Resume` - Resume documents (stores full markdown text + file path)
- `ResumeChunk` - Text chunks with vector embeddings for semantic search
  - Uses pgvector `Vector(1536)` column for OpenAI text-embedding-3-small embeddings
  - Chunk size: 400 characters, overlap: 100 characters

**Relationships:**
```
Employee (1) -> (N) Resume (1) -> (N) ResumeChunk
```

### Vector Search

Semantic search is implemented in `app/services/semantic_search.py`:
- Embeds query using OpenAI text-embedding-3-small
- Uses pgvector's cosine similarity (`<=>` operator) for nearest neighbor search
- Returns top-k matching resume chunks with employee metadata

### API Structure

- `app/main.py` - FastAPI application entry point
- `app/api/v1/routes.py` - Router aggregation
- `app/api/v1/search.py` - Search endpoints:
  - `POST /api/v1/search/semantic` - Direct semantic search (no agent)
  - `POST /api/v1/search/rag-agent` - Full agent pipeline with intent routing

### Chainlit Chat UI

The Chainlit UI provides a conversational interface to interact with the RAG agent.

**Architecture:**
- Runs as a separate Docker container (`chainlit` service)
- Communicates with FastAPI backend via HTTP (decoupled architecture)
- Uses separate dependencies to avoid version conflicts with main application

**Files:**
- `chainlit_app_standalone.py` - Chainlit application that calls FastAPI endpoints
- `requirements-chainlit.txt` - Chainlit-specific dependencies
- `Dockerfile.chainlit` - Separate Dockerfile for Chainlit service

**How it works:**
1. User sends message through Chainlit UI (port 8001)
2. Chainlit app makes HTTP POST to `/api/v1/search/rag-agent`
3. FastAPI invokes the LangGraph agent
4. Agent classifies intent and routes to appropriate node
5. Response is streamed back to Chainlit UI

**Example queries:**
- "Find candidates with Python experience"
- "Show me software engineer resumes"
- "Who is available next week?"
- "Summarize John's resume"
- "What are our talent gaps?"

### Configuration

- `app/core/config.py` - Pydantic Settings for environment variables
- `app/core/constants.py` - Application constants
- Settings loaded from `.env` file

### Ingestion Pipeline

`ingestion/ingest_initial_resumes.py` handles resume processing:
1. Scans `source_files/` for PDF, DOCX, MD files
2. Extracts text (using pdfplumber, python-docx)
3. Splits into chunks (RecursiveCharacterTextSplitter)
4. Generates embeddings (OpenAI text-embedding-3-small)
5. Stores in PostgreSQL with pgvector

**Configuration:**
- `CHUNK_SIZE = 400`
- `CHUNK_OVERLAP = 100`
- `EMBED_MODEL = "text-embedding-3-small"`

## Key Dependencies

**Backend (requirements.txt):**
- **FastAPI** - Web framework
- **LangChain/LangGraph** - Agent orchestration and LLM integration
- **OpenAI** - Embeddings (text-embedding-3-small) and LLM (gpt-4o-mini for intent classification)
- **SQLAlchemy + Alembic** - ORM and migrations
- **pgvector** - Vector similarity search in PostgreSQL
- **pdfplumber, python-docx** - Document parsing

**Chainlit UI (requirements-chainlit.txt):**
- **Chainlit** - Chat UI framework
- **httpx** - Async HTTP client for API communication
- **pydantic** - Data validation (pinned to 2.7.4 for compatibility)

## Development Notes

### Adding New Agent Nodes

1. Create node function in `app/agents/nodes/`
2. Add node to graph in `app/agents/hr_agent.py` using `graph.add_node()`
3. Update intent classifier in `app/agents/nodes/intent.py` if adding new intent
4. Add routing logic in `route_intent()` function
5. Connect node to answer generator with `graph.add_edge()`

### Adding New Tools

Tools are located in `app/agents/tools/`. Current tools:
- `resume_summary_tool.py` - Resume summarization
- `talent_gap_tool.py` - Talent gap analysis
- `calendar_tool.py` - Calendar operations (mock)
- `resume_search.py` - Semantic search tool

### Database Migrations

When modifying models in `db/models/`:
1. Import new models in `db/base.py` to ensure they're detected
2. Run `alembic revision --autogenerate -m "description"`
3. Review generated migration in `alembic/versions/`
4. Apply with `alembic upgrade head`

### Modifying the Chainlit UI

To customize the Chainlit chat interface:

1. **Edit the app:** Modify `chainlit_app_standalone.py`
   - Change welcome message in `on_chat_start()` function
   - Modify message handling in `main()` function
   - Add new Chainlit elements (Text, Image, etc.)

2. **Update dependencies:** Edit `requirements-chainlit.txt` if adding new packages

3. **Rebuild and restart:**
   ```bash
   docker compose build chainlit
   docker compose restart chainlit
   ```

4. **Test locally without Docker:**
   ```bash
   pip install -r requirements-chainlit.txt
   export API_BASE_URL=http://localhost:8000
   chainlit run chainlit_app_standalone.py --port 8001
   ```

**Note:** Chainlit and FastAPI have separate dependency trees. Chainlit uses older FastAPI/Uvicorn versions, which is why it runs in a separate container with isolated dependencies.

### Environment Variables Required

**API Service:**
- `DATABASE_URL` - PostgreSQL connection string
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` - Database credentials
- `OPENAI_API_KEY` - OpenAI API key for embeddings and LLM calls

**Chainlit Service:**
- `API_BASE_URL` - FastAPI backend URL (default: http://api:8000)
