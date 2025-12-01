"""Profile schemas."""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID


class Fact(BaseModel):
    """A fact triple."""
    subject: str
    predicate: str
    object: str
    confidence: float


class ProfileResponse(BaseModel):
    """Response schema for profile."""
    robot_id: str
    entity_type: str
    entity_id: str
    summary: Optional[str] = None
    facts: List[Fact] = []
    last_updated: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "robot_id": "robot-123",
                "entity_type": "user",
                "entity_id": "user-456",
                "summary": "Alice is a frequent user who dislikes loud noises and prefers tea.",
                "facts": [
                    {
                        "subject": "user-456",
                        "predicate": "dislikes",
                        "object": "loud_noises",
                        "confidence": 0.9
                    }
                ],
                "last_updated": "2025-11-21T11:00:00Z"
            }
        }

