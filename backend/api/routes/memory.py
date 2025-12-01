"""Memory query endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.schemas.memory import (
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryAnswerRequest,
    MemoryAnswerResponse
)
from backend.schemas.event import EventDetail
from backend.services.vector_store import VectorStoreService
from backend.services.llm import get_llm_service
from backend.api.dependencies import verify_api_key

router = APIRouter(prefix="/v1/memory", tags=["memory"])


@router.post("/search-events", response_model=MemorySearchResponse)
async def search_events(
    request: MemorySearchRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Search for events using semantic similarity.
    
    This is the RAG primitive - returns relevant events that can be
    used as context for LLM queries.
    """
    vector_store = VectorStoreService(db)
    
    # Extract filters
    time_from = None
    time_to = None
    sources = None
    types = None
    
    if request.filters:
        time_from = request.filters.time_from
        time_to = request.filters.time_to
        sources = request.filters.sources
        types = request.filters.types
    
    # Search for similar events
    results = vector_store.search_similar_events(
        query_text=request.query,
        robot_id=request.robot_id,
        user_id=request.user_id,
        time_from=time_from,
        time_to=time_to,
        sources=sources,
        types=types,
        limit=request.limit
    )
    
    # Convert to response format
    items = []
    for result in results:
        item = EventDetail(
            event_id=result["event_id"],
            robot_id=result["robot_id"],
            user_id=result["user_id"],
            timestamp=result["timestamp"],
            source=result["source"],
            type=result["type"],
            text=result["text"],
            metadata=result["metadata"] if request.include_metadata else None,
            score=result["score"]
        )
        items.append(item)
    
    return MemorySearchResponse(items=items)


@router.post("/answer", response_model=MemoryAnswerResponse)
async def get_memory_answer(
    request: MemoryAnswerRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get an LLM-generated answer based on memory.
    
    This endpoint:
    1. Searches for relevant events
    2. Feeds them to an LLM
    3. Returns a structured answer with supporting evidence
    """
    vector_store = VectorStoreService(db)
    llm_service = get_llm_service()
    
    # Extract time window
    time_from = None
    time_to = None
    if request.time_window:
        time_from = request.time_window.from_
        time_to = request.time_window.to
    
    # Search for relevant events
    events = vector_store.search_similar_events(
        query_text=request.question,
        robot_id=request.robot_id,
        user_id=request.user_id,
        time_from=time_from,
        time_to=time_to,
        limit=request.max_context_events
    )
    
    # Generate answer using LLM
    result = llm_service.generate_answer(
        question=request.question,
        events=events
    )
    
    return MemoryAnswerResponse(
        answer=result["answer"],
        confidence=result["confidence"],
        supporting_events=result["supporting_events"]
    )

