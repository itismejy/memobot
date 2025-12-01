# MemoBot - Memory Layer for Robots

**Semantic memory storage and retrieval system for humanoid robots and AI agents.**

MemoBot provides a complete memory infrastructure that allows robots to:
- 🧠 Remember conversations, observations, and actions
- 🔍 Search memories using natural language
- 💡 Answer questions based on past experiences
- 👤 Build and maintain user profiles with preferences
- ⚡ Provide fast, contextual responses

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [SDK Usage](#sdk-usage)
- [Examples](#examples)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Features

### Core Capabilities

- **Event Ingestion**: Capture speech, vision, actions, and system events
- **Vector Search**: Semantic search over all robot memories using embeddings
- **LLM-Powered Answers**: Get intelligent answers with supporting evidence
- **Profile Management**: Automatic profile building for users, locations, and objects
- **Session Summarization**: Background processing to group and summarize interactions
- **Flexible Storage**: PostgreSQL + pgvector for scalable vector search

### Technical Highlights

- FastAPI-based REST API
- Support for both OpenAI and local embeddings (sentence-transformers)
- Celery workers for background processing
- Docker-compose for easy deployment
- Python SDK for seamless integration
- Full test coverage

## Architecture

```
┌─────────────────────┐
│   Robot / SDK       │
│ (humanoid client)   │
└─────────┬───────────┘
          │ HTTPS (auth, JSON)
          ▼
 ┌───────────────────────┐
 │     API Gateway       │
 └───────┬───────┬──────┘
         │       │
Ingestion│       │ Query
         │       │
  ┌──────▼─┐   ┌─▼────────────────┐
  │ Events │   │  Vector Store    │
  │   DB   │   │  (pgvector)      │
  └────────┘   └──────────────────┘
         │
         ▼
  ┌──────────────┐
  │  Background  │
  │   Workers    │
  └──────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- OpenAI API key (or use local embeddings)

### 1. Clone and Setup

```bash
cd memobot
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 2. Start Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL with pgvector extension
- Redis for task queue
- FastAPI application server
- Celery worker for background tasks

### 3. Verify Installation

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy"}
```

### 4. Use the SDK

```python
from sdk import MemoBotClient

# Initialize client
client = MemoBotClient(
    api_url="http://localhost:8000",
    api_key="your-api-key"
)

# Log an event
client.log_speech(
    robot_id="robot-123",
    text="I don't like loud noises.",
    speaker="user",
    user_id="user-456"
)

# Ask a question
answer = client.ask_memory(
    robot_id="robot-123",
    user_id="user-456",
    question="What are this user's preferences?"
)

print(answer['answer'])
print(f"Confidence: {answer['confidence']}")
```

## API Documentation

### Authentication

All API requests require an `Authorization` header:

```
Authorization: Bearer <API_KEY>
```

### Endpoints

#### POST /v1/events - Ingest Event

```json
{
  "robot_id": "robot-123",
  "user_id": "user-456",
  "source": "speech",
  "type": "USER_SAID",
  "text": "I don't like loud noises.",
  "metadata": {"location": "living_room"}
}
```

#### POST /v1/memory/search-events - Search Memory

```json
{
  "robot_id": "robot-123",
  "query": "What did this user say about noise?",
  "limit": 10
}
```

#### POST /v1/memory/answer - Get LLM Answer

```json
{
  "robot_id": "robot-123",
  "user_id": "user-456",
  "question": "What are this user's preferences?"
}
```

#### GET /v1/memory/profile - Get Profile

```
GET /v1/memory/profile?robot_id=robot-123&entity_type=user&entity_id=user-456
```

Full API documentation available at: http://localhost:8000/docs

## SDK Usage

### Installation

```bash
# From the memobot directory
pip install -e .
```

### Basic Usage

```python
from sdk import MemoBotClient

client = MemoBotClient(
    api_url="http://localhost:8000",
    api_key="your-api-key"
)

# Log different types of events
client.log_speech(robot_id="robot-1", text="Hello", speaker="robot")
client.log_vision(robot_id="robot-1", description="Saw person", objects=["person"])
client.log_action(robot_id="robot-1", action="MOVED", description="Moved forward")

# Search memory
results = client.search_memory(
    robot_id="robot-1",
    query="interactions with users"
)

# Ask questions
answer = client.ask_memory(
    robot_id="robot-1",
    question="What did I do today?"
)

# Get profiles
profile = client.get_profile(
    robot_id="robot-1",
    entity_type="user",
    entity_id="user-123"
)
```

## Examples

### Basic Usage

See [examples/basic_usage.py](examples/basic_usage.py) for a complete example showing:
- Event logging (speech, vision, actions)
- Memory search
- Question answering
- Profile retrieval

Run it:
```bash
python examples/basic_usage.py
```

### ROS Integration

See [examples/ros_integration.py](examples/ros_integration.py) for integrating with ROS-based robots.

## Deployment

### Development

```bash
docker-compose up
```

### Production

1. **Update environment variables**:
   - Set strong `API_SECRET_KEY`
   - Configure production database URL
   - Set appropriate CORS origins

2. **Scale workers**:
   ```bash
   docker-compose up -d --scale worker=3
   ```

3. **Use a reverse proxy** (nginx/traefik) for SSL termination

4. **Enable monitoring** with Prometheus/Grafana

### Configuration

Key environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/memobot

# OpenAI (or use local embeddings)
OPENAI_API_KEY=sk-...
USE_LOCAL_EMBEDDINGS=false

# Redis
REDIS_URL=redis://localhost:6379/0

# Features
ENABLE_SUMMARIZATION=true
ENABLE_PROFILES=true
```

## Development

### Running Tests

```bash
pytest
```

### Local Development Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis separately
# Then start the API
uvicorn backend.api.main:app --reload

# Start worker
celery -A backend.workers.celery_app worker --loglevel=info
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## System Requirements

### Minimum
- 2 CPU cores
- 4GB RAM
- 10GB storage

### Recommended
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ storage (for large event history)

## Performance

- **Ingestion**: ~1000 events/second
- **Search latency**: <100ms for most queries
- **Embedding generation**: ~50ms per event (local) or ~200ms (OpenAI)
- **LLM answers**: 1-3 seconds depending on context size

## Security

- API key authentication required for all endpoints
- SQL injection protection via SQLAlchemy
- CORS configuration for web clients
- Rate limiting (configurable)
- Input validation via Pydantic

## Roadmap

- [ ] Multi-modal embeddings (image + text)
- [ ] Streaming responses for long answers
- [ ] GraphQL API
- [ ] More sophisticated session detection
- [ ] Knowledge graph integration
- [ ] Multi-robot memory sharing
- [ ] Federation for distributed deployments

## License

MIT License - see LICENSE file

## Support

- Documentation: [ARCHITECTURE.md](ARCHITECTURE.md)
- Issues: GitHub Issues
- Discussions: GitHub Discussions

## Acknowledgments

- Built with FastAPI, SQLAlchemy, pgvector
- Embeddings via OpenAI or sentence-transformers
- Inspired by MemGPT, LangChain, and various robotics memory systems

---

**Made with ❤️ for the robotics community**

