"""MemoBot client SDK."""
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List


class MemoBotClient:
    """
    Client for interacting with MemoBot API.
    
    Example usage:
        client = MemoBotClient(
            api_url="https://api.memobot.ai",
            api_key="your-api-key"
        )
        
        # Log an event
        client.log_event(
            robot_id="robot-123",
            source="speech",
            type="USER_SAID",
            text="I don't like loud noises.",
            user_id="user-456"
        )
        
        # Query memory
        answer = client.ask_memory(
            robot_id="robot-123",
            question="What does this user like?",
            user_id="user-456"
        )
    """
    
    def __init__(self, api_url: str, api_key: str):
        """
        Initialize MemoBot client.
        
        Args:
            api_url: Base URL of the MemoBot API
            api_key: API authentication key
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def log_event(
        self,
        robot_id: str,
        source: str,
        type: str,
        text: Optional[str] = None,
        user_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a single event to memory.
        
        Args:
            robot_id: Unique identifier for the robot
            source: Event source (speech, vision, action, system)
            type: Event type (USER_SAID, ROBOT_SAID, etc.)
            text: Text content of the event
            user_id: User identifier (if known)
            timestamp: Event timestamp (defaults to now)
            metadata: Additional metadata
            
        Returns:
            Response with event_id and status
        """
        payload = {
            "robot_id": robot_id,
            "source": source,
            "type": type,
        }
        
        if text:
            payload["text"] = text
        if user_id:
            payload["user_id"] = user_id
        if timestamp:
            payload["timestamp"] = timestamp.isoformat()
        if metadata:
            payload["metadata"] = metadata
        
        response = self.session.post(
            f"{self.api_url}/v1/events",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def log_events_batch(
        self,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Log multiple events in a single request.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Response with results for each event
        """
        response = self.session.post(
            f"{self.api_url}/v1/events/batch",
            json={"events": events}
        )
        response.raise_for_status()
        return response.json()
    
    def search_memory(
        self,
        robot_id: str,
        query: str,
        user_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search memory for relevant events.
        
        Args:
            robot_id: Robot identifier
            query: Natural language query
            user_id: Optional user filter
            filters: Optional filters (time_from, time_to, sources, types)
            limit: Maximum results
            
        Returns:
            Response with matching events
        """
        payload = {
            "robot_id": robot_id,
            "query": query,
            "limit": limit
        }
        
        if user_id:
            payload["user_id"] = user_id
        if filters:
            payload["filters"] = filters
        
        response = self.session.post(
            f"{self.api_url}/v1/memory/search-events",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def ask_memory(
        self,
        robot_id: str,
        question: str,
        user_id: Optional[str] = None,
        time_window: Optional[Dict[str, str]] = None,
        max_context_events: int = 20
    ) -> Dict[str, Any]:
        """
        Ask a question and get an LLM-generated answer based on memory.
        
        Args:
            robot_id: Robot identifier
            question: Natural language question
            user_id: Optional user filter
            time_window: Optional time window (from, to)
            max_context_events: Maximum events for context
            
        Returns:
            Response with answer, confidence, and supporting events
        """
        payload = {
            "robot_id": robot_id,
            "question": question,
            "max_context_events": max_context_events
        }
        
        if user_id:
            payload["user_id"] = user_id
        if time_window:
            payload["time_window"] = time_window
        
        response = self.session.post(
            f"{self.api_url}/v1/memory/answer",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_profile(
        self,
        robot_id: str,
        entity_type: str,
        entity_id: str
    ) -> Dict[str, Any]:
        """
        Get profile for a user, location, or object.
        
        Args:
            robot_id: Robot identifier
            entity_type: Type of entity (user, location, object)
            entity_id: Entity identifier
            
        Returns:
            Profile with summary and facts
        """
        response = self.session.get(
            f"{self.api_url}/v1/memory/profile",
            params={
                "robot_id": robot_id,
                "entity_type": entity_type,
                "entity_id": entity_id
            }
        )
        response.raise_for_status()
        return response.json()
    
    # Convenience methods
    
    def log_speech(
        self,
        robot_id: str,
        text: str,
        speaker: str,
        user_id: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log a speech event (user or robot said something)."""
        event_type = "USER_SAID" if speaker == "user" else "ROBOT_SAID"
        metadata = {}
        if location:
            metadata["location"] = location
        
        return self.log_event(
            robot_id=robot_id,
            source="speech",
            type=event_type,
            text=text,
            user_id=user_id,
            metadata=metadata
        )
    
    def log_vision(
        self,
        robot_id: str,
        description: str,
        objects: Optional[List[str]] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log a vision event (robot saw something)."""
        metadata = {}
        if objects:
            metadata["objects"] = objects
        if location:
            metadata["location"] = location
        
        return self.log_event(
            robot_id=robot_id,
            source="vision",
            type="OBJECT_DETECTED",
            text=description,
            metadata=metadata
        )
    
    def log_action(
        self,
        robot_id: str,
        action: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Log a robot action."""
        return self.log_event(
            robot_id=robot_id,
            source="action",
            type=action,
            text=description,
            metadata=metadata
        )

