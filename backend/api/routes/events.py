"""Event ingestion endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from backend.db.database import get_db
from backend.db.models import Event
from backend.schemas.event import (
    EventCreate,
    EventResponse,
    EventBatchCreate,
    EventBatchResponse
)
from backend.services.embedding import get_embedding_service
from backend.api.dependencies import verify_api_key

router = APIRouter(prefix="/v1/events", tags=["events"])


@router.post("", response_model=EventResponse)
async def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Ingest a single event from a robot.
    
    Creates an event record and generates its embedding for semantic search.
    """
    # Set timestamp if not provided
    timestamp = event.timestamp or datetime.utcnow()
    
    # Create event record
    db_event = Event(
        robot_id=event.robot_id,
        user_id=event.user_id,
        timestamp=timestamp,
        source=event.source,
        type=event.type,
        text=event.text,
        metadata=event.metadata
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # Generate embedding asynchronously (in background in production)
    if event.text:
        embedding_service = get_embedding_service()
        embedding = embedding_service.embed(event.text)
        if embedding:
            db_event.embedding = embedding
            db.commit()
    
    return EventResponse(
        event_id=db_event.event_id,
        status="ok"
    )


@router.post("/batch", response_model=EventBatchResponse)
async def create_events_batch(
    batch: EventBatchCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Ingest multiple events in a single request.
    
    Useful for batching events from robots that collect data offline.
    """
    results = []
    embedding_service = get_embedding_service()
    
    for idx, event in enumerate(batch.events):
        try:
            # Set timestamp if not provided
            timestamp = event.timestamp or datetime.utcnow()
            
            # Create event record
            db_event = Event(
                robot_id=event.robot_id,
                user_id=event.user_id,
                timestamp=timestamp,
                source=event.source,
                type=event.type,
                text=event.text,
                metadata=event.metadata
            )
            
            db.add(db_event)
            db.flush()  # Get event_id without committing
            
            # Generate embedding
            if event.text:
                embedding = embedding_service.embed(event.text)
                if embedding:
                    db_event.embedding = embedding
            
            results.append({
                "index": idx,
                "event_id": str(db_event.event_id),
                "status": "ok"
            })
        
        except Exception as e:
            results.append({
                "index": idx,
                "event_id": None,
                "status": "error",
                "error": str(e)
            })
    
    db.commit()
    
    return EventBatchResponse(results=results)

