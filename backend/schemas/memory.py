"""Memory query schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from backend.schemas.event import EventDetail


class SearchFilters(BaseModel):
    """Filters for memory search."""
    time_from: Optional[datetime] = None
    time_to: Optional[datetime] = None
    sources: Optional[List[str]] = None
    types: Optional[List[str]] = None


class MemorySearchRequest(BaseModel):
    """Request schema for memory search."""
    robot_id: str
    user_id: Optional[str] = None
    query: str = Field(..., description="Natural language query")
    filters: Optional[SearchFilters] = None
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    include_metadata: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "robot_id": "robot-123",
                "user_id": "user-456",
                "query": "What did this user say about noise preferences?",
                "filters": {
                    "time_from": "2025-11-01T00:00:00Z",
                    "sources": ["speech"],
                    "types": ["USER_SAID"]
                },
                "limit": 10
            }
        }


class MemorySearchResponse(BaseModel):
    """Response schema for memory search."""
    items: List[EventDetail]


class TimeWindow(BaseModel):
    """Time window filter."""
    from_: Optional[datetime] = Field(None, alias="from")
    to: Optional[datetime] = None


class MemoryAnswerRequest(BaseModel):
    """Request schema for LLM-powered answer."""
    robot_id: str
    user_id: Optional[str] = None
    question: str = Field(..., description="Natural language question")
    time_window: Optional[TimeWindow] = None
    max_context_events: int = Field(20, ge=1, le=100, description="Maximum events for context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "robot_id": "robot-123",
                "user_id": "user-456",
                "question": "What are this user's preferences about noise and drinks?",
                "time_window": {
                    "from": "2025-10-01T00:00:00Z",
                    "to": "2025-11-21T23:59:59Z"
                }
            }
        }


class SupportingEvent(BaseModel):
    """Supporting event for an answer."""
    event_id: str
    timestamp: datetime
    text: Optional[str]


class MemoryAnswerResponse(BaseModel):
    """Response schema for LLM answer."""
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    supporting_events: List[SupportingEvent]

