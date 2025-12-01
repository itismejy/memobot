# MemoBot Architecture Documentation

## Overview

MemoBot is a semantic memory layer designed for humanoid robots and AI agents. It provides persistent, searchable memory with intelligent retrieval and summarization capabilities.

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         Robot / Client                          │
│                      (uses SDK or REST API)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS + Bearer Token
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                        API Gateway                              │
│                     (FastAPI Application)                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  Event Ingestion │  │  Memory Queries  │  │  Profiles    │ │
│  │   /v1/events     │  │  /v1/memory/*    │  │              │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└────────────────┬────────────────┬────────────────┬─────────────┘
                 │                │                │
                 ▼                ▼                ▼
┌────────────────────────────────────────────────────────────────┐
│                     Services Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Embedding   │  │ Vector Store │  │    LLM Service       │ │
│  │  Service     │  │   Service    │  │  (Summarization)     │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└────────────────┬────────────────┬────────────────┬─────────────┘
                 │                │                │
                 ▼                ▼                ▼
┌────────────────────────────────────────────────────────────────┐
│                     Storage Layer                              │
│  ┌──────────────────┐           ┌─────────────────────────┐   │
│  │   PostgreSQL     │           │      Redis              │   │
│  │  + pgvector      │           │  (Task Queue/Cache)     │   │
│  │                  │           └─────────────────────────┘   │
│  │  - events        │                                          │
│  │  - sessions      │                                          │
│  │  - profiles      │                                          │
│  │  - embeddings    │                                          │
│  └──────────────────┘                                          │
└────────────────────────────────────────────────────────────────┘
                 ▲
                 │ Periodic Tasks
                 │
┌────────────────┴────────────────────────────────────────────────┐
│                   Background Workers                            │
│                     (Celery Workers)                            │
│  ┌──────────────────┐           ┌─────────────────────────┐    │
│  │  Session         │           │  Profile                │    │
│  │  Summarization   │           │  Updates                │    │
│  └──────────────────┘           └─────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Data Model

### Core Tables

#### 1. Events Table

The central log of everything the robot observes and does.

```sql
events (
  event_id      UUID PRIMARY KEY,
  robot_id      TEXT NOT NULL,
  user_id       TEXT NULL,
  timestamp     TIMESTAMPTZ NOT NULL,
  source        TEXT NOT NULL,     -- 'speech', 'vision', 'system', 'action'
  type          TEXT NOT NULL,     -- 'USER_SAID', 'ROBOT_SAID', etc.
  text          TEXT NULL,
  metadata      JSONB,
  session_id    UUID NULL,
  embedding     VECTOR(384),       -- pgvector type
  created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_robot_user_timestamp ON events(robot_id, user_id, timestamp);
CREATE INDEX idx_robot_timestamp ON events(robot_id, timestamp);
CREATE INDEX idx_session_timestamp ON events(session_id, timestamp);
```

**Fields:**
- `event_id`: Unique identifier
- `robot_id`: Which robot created this event
- `user_id`: Associated user (if applicable)
- `timestamp`: When the event occurred
- `source`: Category of event source
- `type`: Specific event type
- `text`: Textual content (for embedding)
- `metadata`: Flexible JSON for extra data (location, objects, etc.)
- `session_id`: Groups related events
- `embedding`: Vector representation for semantic search

#### 2. Sessions Table

Groups of related events (conversations, interactions).

```sql
sessions (
  session_id    UUID PRIMARY KEY,
  robot_id      TEXT NOT NULL,
  user_id       TEXT NULL,
  start_time    TIMESTAMPTZ NOT NULL,
  end_time      TIMESTAMPTZ NOT NULL,
  summary       TEXT,
  metadata      JSONB,
  created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_robot_user_time ON sessions(robot_id, user_id, start_time);
```

**Purpose:**
- Group events that belong together
- Provide summaries of interactions
- Enable fast retrieval of conversation history

#### 3. Profiles Table

Persistent knowledge about entities (users, locations, objects).

```sql
profiles (
  profile_id    UUID PRIMARY KEY,
  robot_id      TEXT NOT NULL,
  entity_type   TEXT NOT NULL,    -- 'user', 'location', 'object'
  entity_id     TEXT NOT NULL,
  summary       TEXT,
  facts         JSONB,             -- [{subject, predicate, object, confidence}]
  last_updated  TIMESTAMPTZ NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE UNIQUE INDEX idx_robot_entity ON profiles(robot_id, entity_type, entity_id);
```

**Purpose:**
- Cache stable knowledge about entities
- Fast lookup without searching all events
- Confidence-weighted facts

## API Layer

### Authentication

All endpoints require Bearer token authentication:

```
Authorization: Bearer <API_KEY>
```

In production, implement proper API key management:
- Store hashed keys in database
- Rate limiting per key
- Key rotation
- Scope-based permissions

### Endpoint Design

#### Ingestion Endpoints

**POST /v1/events**
- Accepts single event
- Validates schema
- Stores in database
- Generates embedding (async)
- Returns event_id

**POST /v1/events/batch**
- Accepts multiple events
- Optimized for bulk ingestion
- Returns results array

#### Query Endpoints

**POST /v1/memory/search-events**
- RAG primitive
- Semantic similarity search
- Supports filters (time, source, type)
- Returns ranked events

**POST /v1/memory/answer**
- High-level query interface
- Retrieves relevant events
- Feeds to LLM
- Returns structured answer + evidence

**GET /v1/memory/profile**
- Fast profile lookup
- Creates on-demand if missing
- Returns summary + facts

## Services Layer

### Embedding Service

**Responsibilities:**
- Convert text to vector embeddings
- Support multiple backends (OpenAI, local models)
- Batch processing for efficiency

**Implementation:**
```python
class EmbeddingService:
    def embed(text: str) -> List[float]
    def embed_batch(texts: List[str]) -> List[List[float]]
```

**Backends:**
- **OpenAI**: `text-embedding-3-small` (384 dimensions)
- **Local**: `sentence-transformers/all-MiniLM-L6-v2`

**Performance:**
- OpenAI: ~200ms per request
- Local: ~50ms per text (GPU), ~200ms (CPU)

### Vector Store Service

**Responsibilities:**
- Store embeddings with metadata
- Perform similarity search
- Handle filtering

**Key Operations:**
```python
class VectorStoreService:
    def add_event_embedding(event_id, text) -> bool
    def search_similar_events(query, filters) -> List[Event]
    def get_recent_events(robot_id, limit) -> List[Event]
```

**Search Algorithm:**
- Uses pgvector's cosine distance operator
- Combines vector similarity with SQL filters
- Indexes for fast filtering before similarity computation

### LLM Service

**Responsibilities:**
- Generate answers from events
- Summarize sessions
- Extract facts

**Key Operations:**
```python
class LLMService:
    def generate_answer(question, events) -> Dict
    def summarize_session(events) -> str
    def extract_facts(events, entity_id) -> List[Fact]
```

**Prompting Strategy:**
- System prompt defines role
- Context: Top-K events formatted clearly
- Temperature: 0.3 for factual responses
- Max tokens: 200-500 depending on task

## Background Workers

### Session Summarization Task

**Frequency:** Hourly

**Algorithm:**
1. Find events without session_id (recent 7 days)
2. Group by (robot_id, user_id, time proximity)
3. Time gap threshold: 30 minutes
4. For each group:
   - Create session record
   - Generate LLM summary
   - Update events with session_id

**Why:**
- Reduces redundancy in searches
- Provides high-level view
- Enables conversation-level queries

### Profile Update Task

**Frequency:** Daily

**Algorithm:**
1. Find entities with recent activity (24 hours)
2. For each entity:
   - Retrieve recent events (limit 50)
   - Generate summary
   - Extract facts
   - Update or create profile

**Why:**
- Keeps profiles fresh
- Amortizes LLM cost
- Fast profile lookups

## Scaling Considerations

### Horizontal Scaling

**API Layer:**
- Stateless FastAPI instances
- Load balance with nginx/traefik
- Auto-scale based on request rate

**Workers:**
- Multiple Celery workers
- Task routing by type
- Priority queues

**Database:**
- Read replicas for queries
- Connection pooling
- Partition events table by time

### Vertical Scaling

**Memory:**
- Event volume: ~1KB per event
- 1M events ≈ 1GB (events + embeddings)
- Profiles: ~10KB each

**CPU:**
- Embedding generation (if local)
- Vector similarity computation
- LLM inference (if local)

### Caching Strategy

**Redis Caching:**
- Profile cache (TTL: 1 hour)
- Recent events cache (TTL: 5 minutes)
- Search result cache (TTL: 1 minute)

## Security

### API Security

1. **Authentication**: Bearer tokens
2. **Rate Limiting**: Per-key limits
3. **Input Validation**: Pydantic schemas
4. **SQL Injection**: Parameterized queries (SQLAlchemy)

### Data Privacy

1. **User Data**: Store only necessary fields
2. **Encryption**: At-rest (database level)
3. **Retention**: Configurable data retention policies
4. **GDPR**: Support for data export/deletion

## Monitoring

### Key Metrics

**API Metrics:**
- Request rate by endpoint
- Response time (p50, p95, p99)
- Error rate
- Authentication failures

**Storage Metrics:**
- Event count
- Database size
- Vector index size
- Query latency

**Worker Metrics:**
- Task queue length
- Task processing time
- Success/failure rate
- Worker health

### Logging

**Structured Logging:**
```python
{
  "timestamp": "2025-11-22T10:00:00Z",
  "level": "INFO",
  "service": "api",
  "robot_id": "robot-123",
  "endpoint": "/v1/events",
  "duration_ms": 45
}
```

## Testing Strategy

### Unit Tests
- Services (embedding, vector store, LLM)
- API endpoints
- Data models

### Integration Tests
- End-to-end API flows
- Database operations
- Worker tasks

### Performance Tests
- Load testing (k6, locust)
- Embedding generation throughput
- Search latency under load

## Future Enhancements

### Short Term
- [ ] Webhook support for real-time notifications
- [ ] Streaming responses for long answers
- [ ] Multi-tenant support
- [ ] Advanced analytics dashboard

### Medium Term
- [ ] Multi-modal embeddings (image + text)
- [ ] Knowledge graph integration
- [ ] Federated learning across robots
- [ ] Compression for old events

### Long Term
- [ ] Edge deployment (on-robot inference)
- [ ] Multi-robot memory sharing
- [ ] Causal reasoning
- [ ] Continuous learning from feedback

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Celery Documentation](https://docs.celeryq.dev/)

