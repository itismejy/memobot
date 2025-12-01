"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from backend.api.main import app
from backend.db.database import Base, engine

# Test client
client = TestClient(app)

# Test API key
TEST_API_KEY = "test-api-key-123"
HEADERS = {"Authorization": f"Bearer {TEST_API_KEY}"}


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Setup test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "MemoBot API"
    assert data["status"] == "online"


def test_create_event():
    """Test creating a single event."""
    event_data = {
        "robot_id": "test-robot-1",
        "user_id": "test-user-1",
        "source": "speech",
        "type": "USER_SAID",
        "text": "Test event",
        "metadata": {"location": "test_room"}
    }
    
    response = client.post("/v1/events", json=event_data, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "event_id" in data
    assert data["status"] == "ok"


def test_create_event_batch():
    """Test creating multiple events."""
    batch_data = {
        "events": [
            {
                "robot_id": "test-robot-1",
                "source": "speech",
                "type": "USER_SAID",
                "text": "Event 1"
            },
            {
                "robot_id": "test-robot-1",
                "source": "speech",
                "type": "USER_SAID",
                "text": "Event 2"
            }
        ]
    }
    
    response = client.post("/v1/events/batch", json=batch_data, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2
    assert all(r["status"] == "ok" for r in data["results"])


def test_search_events():
    """Test searching events."""
    # First create some events
    for i in range(3):
        client.post(
            "/v1/events",
            json={
                "robot_id": "test-robot-2",
                "source": "speech",
                "type": "USER_SAID",
                "text": f"Search test event {i}"
            },
            headers=HEADERS
        )
    
    # Search for events
    search_data = {
        "robot_id": "test-robot-2",
        "query": "search test",
        "limit": 10
    }
    
    response = client.post("/v1/memory/search-events", json=search_data, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


def test_memory_answer():
    """Test getting an LLM answer."""
    # Create some events
    client.post(
        "/v1/events",
        json={
            "robot_id": "test-robot-3",
            "user_id": "test-user-3",
            "source": "speech",
            "type": "USER_SAID",
            "text": "I like tea"
        },
        headers=HEADERS
    )
    
    # Ask a question
    answer_data = {
        "robot_id": "test-robot-3",
        "user_id": "test-user-3",
        "question": "What does this user like?"
    }
    
    response = client.post("/v1/memory/answer", json=answer_data, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "confidence" in data
    assert "supporting_events" in data


def test_get_profile():
    """Test getting a user profile."""
    robot_id = "test-robot-4"
    user_id = "test-user-4"
    
    # Create some events first
    for text in ["I like quiet places", "I prefer tea", "I enjoy reading"]:
        client.post(
            "/v1/events",
            json={
                "robot_id": robot_id,
                "user_id": user_id,
                "source": "speech",
                "type": "USER_SAID",
                "text": text
            },
            headers=HEADERS
        )
    
    # Get profile
    response = client.get(
        "/v1/memory/profile",
        params={
            "robot_id": robot_id,
            "entity_type": "user",
            "entity_id": user_id
        },
        headers=HEADERS
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["robot_id"] == robot_id
    assert data["entity_type"] == "user"
    assert data["entity_id"] == user_id
    assert "summary" in data
    assert "facts" in data


def test_authentication_required():
    """Test that authentication is required."""
    response = client.post(
        "/v1/events",
        json={
            "robot_id": "test",
            "source": "speech",
            "type": "TEST",
            "text": "test"
        }
    )
    assert response.status_code == 401

