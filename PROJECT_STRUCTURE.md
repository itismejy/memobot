# MemoBot Project Structure

```
memobot/
│
├── 📄 README.md                      # Main documentation
├── 📄 ARCHITECTURE.md                # Technical architecture details
├── 📄 QUICKSTART.md                  # 5-minute setup guide
├── 📄 IMPLEMENTATION_SUMMARY.md      # What was built
├── 📄 PROJECT_STRUCTURE.md           # This file
│
├── 🐳 docker-compose.yml             # Docker orchestration
├── 🐳 Dockerfile                     # Container definition
├── 📦 requirements.txt               # Python dependencies
├── 📦 setup.py                       # Package setup
├── 🔨 Makefile                       # Dev commands
├── 🙈 .gitignore                     # Git ignore rules
├── 📝 .env.example                   # Environment template
│
├── 🖥️  backend/                      # Backend services
│   ├── __init__.py
│   ├── config.py                     # Configuration management
│   │
│   ├── 🌐 api/                       # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py                   # Main FastAPI app
│   │   ├── dependencies.py           # Auth & dependencies
│   │   └── routes/                   # API endpoints
│   │       ├── __init__.py
│   │       ├── events.py             # Event ingestion
│   │       ├── memory.py             # Memory queries
│   │       └── profiles.py           # Profile management
│   │
│   ├── 🗄️  db/                       # Database layer
│   │   ├── __init__.py
│   │   ├── database.py               # Connection & session
│   │   └── models.py                 # SQLAlchemy models
│   │
│   ├── 📋 schemas/                   # Pydantic validation
│   │   ├── __init__.py
│   │   ├── event.py                  # Event schemas
│   │   ├── memory.py                 # Memory query schemas
│   │   └── profile.py                # Profile schemas
│   │
│   ├── ⚙️  services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── embedding.py              # Vector embeddings
│   │   ├── vector_store.py           # Semantic search
│   │   └── llm.py                    # LLM integration
│   │
│   └── 👷 workers/                   # Background tasks
│       ├── __init__.py
│       ├── celery_app.py             # Celery configuration
│       └── tasks.py                  # Async tasks
│
├── 🐍 sdk/                           # Python SDK
│   ├── __init__.py
│   └── client.py                     # MemoBotClient
│
├── 💡 examples/                      # Usage examples
│   ├── __init__.py
│   ├── basic_usage.py                # Basic SDK usage
│   └── ros_integration.py            # ROS integration
│
└── 🧪 tests/                         # Test suite
    ├── __init__.py
    ├── test_api.py                   # API tests
    └── test_sdk.py                   # SDK tests
```

## File Count Summary

- **Total Files**: 40+
- **Python Files**: 30
- **Documentation**: 5
- **Configuration**: 5
- **Examples**: 2
- **Tests**: 2

## Key Components

### 1️⃣ API Layer (backend/api/)
- **main.py**: FastAPI application with lifecycle management
- **routes/**: RESTful endpoints matching design spec
  - Events ingestion (single & batch)
  - Memory search (semantic)
  - Memory answer (LLM-powered)
  - Profile retrieval

### 2️⃣ Database Layer (backend/db/)
- **models.py**: SQLAlchemy ORM models
  - Event (with pgvector embedding)
  - Session (conversation groups)
  - Profile (entity knowledge)
- **database.py**: Connection pooling & session management

### 3️⃣ Services Layer (backend/services/)
- **embedding.py**: Text → Vector conversion
  - OpenAI API support
  - Local model support (sentence-transformers)
- **vector_store.py**: Semantic search operations
  - pgvector integration
  - Filtered similarity search
- **llm.py**: LLM-powered operations
  - Answer generation
  - Summarization
  - Fact extraction

### 4️⃣ Background Workers (backend/workers/)
- **tasks.py**: Celery tasks
  - Session summarization (hourly)
  - Profile updates (daily)
- **celery_app.py**: Task queue configuration

### 5️⃣ SDK (sdk/)
- **client.py**: MemoBotClient
  - Simple API wrapper
  - Convenience methods
  - Type hints

### 6️⃣ Examples (examples/)
- **basic_usage.py**: Complete workflow demo
- **ros_integration.py**: ROS bridge pattern

### 7️⃣ Tests (tests/)
- **test_api.py**: API endpoint tests
- **test_sdk.py**: SDK client tests

## Code Statistics

### Lines of Code (Approximate)

| Component | Files | Lines |
|-----------|-------|-------|
| Backend API | 6 | ~600 |
| Database Models | 2 | ~150 |
| Services | 3 | ~600 |
| Workers | 2 | ~250 |
| SDK | 1 | ~300 |
| Examples | 2 | ~350 |
| Tests | 2 | ~250 |
| **Total** | **18** | **~2,500** |

### Documentation

| File | Lines | Purpose |
|------|-------|---------|
| README.md | ~300 | Main docs |
| ARCHITECTURE.md | ~400 | Technical deep dive |
| QUICKSTART.md | ~150 | Quick setup |
| IMPLEMENTATION_SUMMARY.md | ~200 | What was built |
| **Total** | **~1,050** | Full coverage |

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL + pgvector
- **ORM**: SQLAlchemy 2.0
- **Task Queue**: Celery + Redis
- **Embeddings**: OpenAI / sentence-transformers
- **LLM**: OpenAI GPT-4o-mini

### SDK
- **Language**: Python 3.11+
- **HTTP**: requests library
- **Type Hints**: Full coverage

### Infrastructure
- **Container**: Docker
- **Orchestration**: Docker Compose
- **Reverse Proxy**: (nginx/traefik - user's choice)

## Development Workflow

```
┌─────────────────────────────────────────────┐
│           Development Cycle                 │
├─────────────────────────────────────────────┤
│                                             │
│  1. make install      # Install deps       │
│  2. make docker-up    # Start services     │
│  3. make example      # Run example        │
│  4. make test         # Run tests          │
│  5. make lint         # Check code         │
│  6. make format       # Format code        │
│                                             │
└─────────────────────────────────────────────┘
```

## Deployment Workflow

```
┌─────────────────────────────────────────────┐
│           Production Deploy                 │
├─────────────────────────────────────────────┤
│                                             │
│  1. Configure .env    # Set secrets        │
│  2. make docker-build # Build images       │
│  3. make docker-up    # Start stack        │
│  4. make scale-workers N=3 # Scale         │
│                                             │
└─────────────────────────────────────────────┘
```

## API Endpoints Overview

```
GET  /                           # Service info
GET  /health                     # Health check
GET  /docs                       # OpenAPI docs

POST /v1/events                  # Ingest single event
POST /v1/events/batch            # Ingest batch events

POST /v1/memory/search-events    # Semantic search
POST /v1/memory/answer           # LLM Q&A
GET  /v1/memory/profile          # Get profile
```

## Database Schema

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   events     │      │   sessions   │      │   profiles   │
├──────────────┤      ├──────────────┤      ├──────────────┤
│ event_id     │──┐   │ session_id   │      │ profile_id   │
│ robot_id     │  │   │ robot_id     │      │ robot_id     │
│ user_id      │  │   │ user_id      │      │ entity_type  │
│ timestamp    │  │   │ start_time   │      │ entity_id    │
│ source       │  │   │ end_time     │      │ summary      │
│ type         │  │   │ summary      │      │ facts (JSON) │
│ text         │  │   │ metadata     │      │ last_updated │
│ metadata     │  │   └──────────────┘      └──────────────┘
│ session_id   │◄─┘
│ embedding    │
│ created_at   │
└──────────────┘
```

## Quick Commands Reference

```bash
# Start everything
make docker-up

# Run example
make example

# View logs
make docker-logs

# Run tests
make test

# Access database
make db-shell

# Scale workers
make scale-workers N=5

# Restart API
make restart-api

# Clean up
make docker-clean
```

## Success Criteria ✅

- [x] Matches design document specification
- [x] All endpoints implemented
- [x] Vector search working
- [x] LLM integration complete
- [x] Background workers functional
- [x] SDK fully featured
- [x] Examples provided
- [x] Tests written
- [x] Documentation comprehensive
- [x] Docker deployment ready
- [x] Production-ready architecture

**Status: COMPLETE AND READY TO USE! 🎉**

