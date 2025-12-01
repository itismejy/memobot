# MemoBot Quick Start Guide

Get MemoBot running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- Python 3.11+ (for SDK usage)
- OpenAI API key (optional - can use local embeddings)

## Step 1: Initial Setup (2 minutes)

```bash
# Navigate to memobot directory
cd memobot

# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or your preferred editor
```

In `.env`, set at minimum:
```bash
OPENAI_API_KEY=sk-your-key-here
# OR use local embeddings:
USE_LOCAL_EMBEDDINGS=true
```

## Step 2: Start Services (1 minute)

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

You should see:
- ✅ postgres (healthy)
- ✅ redis (running)
- ✅ api (running on port 8000)
- ✅ worker (running)

## Step 3: Verify Installation (30 seconds)

```bash
# Health check
curl http://localhost:8000/health

# Should return: {"status":"healthy"}

# View API docs
open http://localhost:8000/docs
```

## Step 4: Run Example (1 minute)

```bash
# Install SDK
pip install requests

# Run basic example
python examples/basic_usage.py
```

You should see:
```
==========================================================
MemoBot SDK - Basic Usage Example
==========================================================

1. Logging speech events...
  ✓ Logged: 'I don't like loud noises...' [ID: ...]
  ✓ Logged: 'Could I have tea instead of coffee?...' [ID: ...]
  ...

5. Asking memory a question...
  Answer: The user dislikes loud noises and prefers tea over coffee...
  Confidence: 0.88
```

## Step 5: Use in Your Code (30 seconds)

```python
from sdk import MemoBotClient

# Initialize
client = MemoBotClient(
    api_url="http://localhost:8000",
    api_key="demo-key"
)

# Log what your robot sees/hears
client.log_speech(
    robot_id="my-robot",
    text="Hello, I'm here!",
    speaker="user",
    user_id="alice"
)

# Query memory
answer = client.ask_memory(
    robot_id="my-robot",
    user_id="alice",
    question="What did Alice say?"
)

print(answer['answer'])
```

## Common Issues & Solutions

### Issue: "Connection refused" error

**Solution:** Make sure services are running:
```bash
docker-compose ps
docker-compose logs api
```

### Issue: Embeddings are slow

**Solution:** Switch to local embeddings:
```bash
# In .env
USE_LOCAL_EMBEDDINGS=true
```

### Issue: OpenAI API errors

**Solution:** Check your API key:
```bash
# Test your key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Issue: Out of memory

**Solution:** Reduce batch sizes in `.env`:
```bash
SUMMARIZATION_BATCH_SIZE=50  # default is 100
```

## Next Steps

1. **Read the full README**: [README.md](README.md)
2. **Explore architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Try ROS integration**: [examples/ros_integration.py](examples/ros_integration.py)
4. **Check API docs**: http://localhost:8000/docs

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v
```

## Production Deployment

For production, see the Deployment section in [README.md](README.md#deployment).

Key changes needed:
1. Set strong `API_SECRET_KEY`
2. Use production database
3. Enable SSL/TLS
4. Configure rate limiting
5. Set up monitoring

## Getting Help

- Check logs: `docker-compose logs -f api`
- View worker logs: `docker-compose logs -f worker`
- Database logs: `docker-compose logs -f postgres`

## Useful Commands

```bash
# View all logs
docker-compose logs -f

# Restart API only
docker-compose restart api

# Scale workers
docker-compose up -d --scale worker=3

# Access database
docker-compose exec postgres psql -U postgres -d memobot

# Run shell in API container
docker-compose exec api bash

# View Redis queue
docker-compose exec redis redis-cli
```

Happy building! 🤖✨

