"""Profile management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from backend.db.database import get_db
from backend.db.models import Profile
from backend.schemas.profile import ProfileResponse, Fact
from backend.services.vector_store import VectorStoreService
from backend.services.llm import get_llm_service
from backend.api.dependencies import verify_api_key

router = APIRouter(prefix="/v1/memory", tags=["profiles"])


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    robot_id: str = Query(..., description="Robot identifier"),
    entity_type: str = Query(..., description="Entity type: user, location, object"),
    entity_id: str = Query(..., description="Entity identifier"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get or create a profile for an entity.
    
    Returns stable, summarized knowledge about users, locations, or objects
    that the robot has interacted with.
    """
    # Look up existing profile
    profile = db.query(Profile).filter(
        Profile.robot_id == robot_id,
        Profile.entity_type == entity_type,
        Profile.entity_id == entity_id
    ).first()
    
    if not profile:
        # Create a new profile by analyzing events
        profile = await _create_profile(
            db=db,
            robot_id=robot_id,
            entity_type=entity_type,
            entity_id=entity_id
        )
    
    # Convert facts from JSON to Fact objects
    facts = []
    if profile.facts:
        facts = [Fact(**fact) for fact in profile.facts]
    
    return ProfileResponse(
        robot_id=profile.robot_id,
        entity_type=profile.entity_type,
        entity_id=profile.entity_id,
        summary=profile.summary,
        facts=facts,
        last_updated=profile.last_updated
    )


async def _create_profile(
    db: Session,
    robot_id: str,
    entity_type: str,
    entity_id: str
) -> Profile:
    """Create a new profile by analyzing events."""
    vector_store = VectorStoreService(db)
    llm_service = get_llm_service()
    
    # Get recent events for this entity
    user_id = entity_id if entity_type == "user" else None
    events = vector_store.get_recent_events(
        robot_id=robot_id,
        user_id=user_id,
        limit=50
    )
    
    # Convert events to dict format
    event_dicts = [
        {
            "event_id": str(e.event_id),
            "text": e.text,
            "type": e.type,
            "timestamp": e.timestamp
        }
        for e in events
        if e.text
    ]
    
    # Generate summary
    summary = llm_service.summarize_session(event_dicts)
    
    # Extract facts
    facts = llm_service.extract_facts(event_dicts, entity_id)
    
    # Create profile
    profile = Profile(
        robot_id=robot_id,
        entity_type=entity_type,
        entity_id=entity_id,
        summary=summary,
        facts=facts,
        last_updated=datetime.utcnow()
    )
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile

