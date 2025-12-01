"""Tests for SDK client."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from sdk import MemoBotClient


@pytest.fixture
def mock_client():
    """Create a mock client."""
    with patch('sdk.client.requests.Session') as mock_session:
        client = MemoBotClient(
            api_url="http://test.example.com",
            api_key="test-key"
        )
        yield client, mock_session


def test_client_initialization():
    """Test client initialization."""
    client = MemoBotClient(
        api_url="http://test.example.com",
        api_key="test-key"
    )
    
    assert client.api_url == "http://test.example.com"
    assert client.api_key == "test-key"
    assert "Authorization" in client.session.headers


def test_log_event(mock_client):
    """Test logging a single event."""
    client, mock_session = mock_client
    
    mock_response = Mock()
    mock_response.json.return_value = {"event_id": "123", "status": "ok"}
    mock_session.return_value.post.return_value = mock_response
    
    result = client.log_event(
        robot_id="robot-1",
        source="speech",
        type="USER_SAID",
        text="Test"
    )
    
    assert result["status"] == "ok"


def test_log_speech(mock_client):
    """Test convenience method for logging speech."""
    client, mock_session = mock_client
    
    mock_response = Mock()
    mock_response.json.return_value = {"event_id": "123", "status": "ok"}
    mock_session.return_value.post.return_value = mock_response
    
    result = client.log_speech(
        robot_id="robot-1",
        text="Hello",
        speaker="user",
        user_id="user-1"
    )
    
    assert result["status"] == "ok"


def test_search_memory(mock_client):
    """Test searching memory."""
    client, mock_session = mock_client
    
    mock_response = Mock()
    mock_response.json.return_value = {"items": []}
    mock_session.return_value.post.return_value = mock_response
    
    result = client.search_memory(
        robot_id="robot-1",
        query="test query"
    )
    
    assert "items" in result


def test_ask_memory(mock_client):
    """Test asking a question."""
    client, mock_session = mock_client
    
    mock_response = Mock()
    mock_response.json.return_value = {
        "answer": "Test answer",
        "confidence": 0.9,
        "supporting_events": []
    }
    mock_session.return_value.post.return_value = mock_response
    
    result = client.ask_memory(
        robot_id="robot-1",
        question="What happened?"
    )
    
    assert "answer" in result
    assert "confidence" in result


def test_get_profile(mock_client):
    """Test getting a profile."""
    client, mock_session = mock_client
    
    mock_response = Mock()
    mock_response.json.return_value = {
        "robot_id": "robot-1",
        "entity_type": "user",
        "entity_id": "user-1",
        "summary": "Test user",
        "facts": []
    }
    mock_session.return_value.get.return_value = mock_response
    
    result = client.get_profile(
        robot_id="robot-1",
        entity_type="user",
        entity_id="user-1"
    )
    
    assert result["entity_type"] == "user"
    assert "summary" in result

