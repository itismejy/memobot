"""Event schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID


class EventCreate(BaseModel):
    """Schema for creating a new event."""
    robot_id: str = Field(..., description="Unique identifier for the robot")
    user_id: Optional[str] = Field(None, description="User identifier (if known)")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp (defaults to now)")
    source: str = Field(..., description="Event source: speech, vision, action, system")
    type: str = Field(..., description="Event type: USER_SAID, ROBOT_SAID, OBJECT_DETECTED, etc.")
    text: Optional[str] = Field(None, description="Text content of the event")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "robot_id": "robot-123",
                "user_id": "user-456",
                "source": "speech",
                "type": "USER_SAID",
                "text": "I don't like loud noises.",
                "metadata": {
                    "location": "living_room",
                    "lang": "en-US"
                }
            }
        }


class EventResponse(BaseModel):
    """Schema for event response."""
    event_id: UUID
    status: str = "ok"


class EventBatchCreate(BaseModel):
    """Schema for batch event creation."""
    events: List[EventCreate]


class EventBatchResponse(BaseModel):
    """Schema for batch event response."""
    results: List[Dict[str, Any]]


class EventDetail(BaseModel):
    """Detailed event information."""
    event_id: UUID
    robot_id: str
    user_id: Optional[str]
    timestamp: datetime
    source: str
    type: str
    text: Optional[str]
    metadata: Optional[Dict[str, Any]]
    score: Optional[float] = None  # Relevance score for search results
    
    class Config:
        from_attributes = True

