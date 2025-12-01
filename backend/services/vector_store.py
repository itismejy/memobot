"""Vector store service for semantic search over events."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from backend.db.models import Event
from backend.services.embedding import get_embedding_service


class VectorStoreService:
    """Service for storing and searching vectors."""
    
    def __init__(self, db: Session):
        """Initialize vector store with database session."""
        self.db = db
        self.embedding_service = get_embedding_service()
    
    def add_event_embedding(self, event_id: str, text: str) -> bool:
        """
        Generate and store embedding for an event.
        
        Args:
            event_id: Event UUID
            text: Text to embed
            
        Returns:
            True if successful
        """
        if not text:
            return False
        
        embedding = self.embedding_service.embed(text)
        if not embedding:
            return False
        
        # Update event with embedding
        event = self.db.query(Event).filter(Event.event_id == event_id).first()
        if event:
            event.embedding = embedding
            self.db.commit()
            return True
        
        return False
    
    def search_similar_events(
        self,
        query_text: str,
        robot_id: str,
        user_id: Optional[str] = None,
        time_from: Optional[datetime] = None,
        time_to: Optional[datetime] = None,
        sources: Optional[List[str]] = None,
        types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for events similar to query text.
        
        Args:
            query_text: Natural language query
            robot_id: Robot identifier
            user_id: Optional user filter
            time_from: Start of time range
            time_to: End of time range
            sources: Event source filters
            types: Event type filters
            limit: Maximum results
            
        Returns:
            List of events with similarity scores
        """
        # Generate query embedding
        query_embedding = self.embedding_service.embed(query_text)
        if not query_embedding:
            return []
        
        # Build query with filters
        query = self.db.query(Event).filter(Event.robot_id == robot_id)
        
        # Apply filters
        if user_id:
            query = query.filter(Event.user_id == user_id)
        
        if time_from:
            query = query.filter(Event.timestamp >= time_from)
        
        if time_to:
            query = query.filter(Event.timestamp <= time_to)
        
        if sources:
            query = query.filter(Event.source.in_(sources))
        
        if types:
            query = query.filter(Event.type.in_(types))
        
        # Only include events with embeddings
        query = query.filter(Event.embedding.isnot(None))
        
        # Calculate cosine similarity and order by it
        # Note: pgvector uses <=> for cosine distance (1 - cosine similarity)
        query = query.order_by(Event.embedding.cosine_distance(query_embedding))
        
        # Limit results
        query = query.limit(limit)
        
        # Execute and format results
        results = []
        for event in query.all():
            # Calculate similarity score (1 - distance)
            distance = self.db.query(
                Event.embedding.cosine_distance(query_embedding)
            ).filter(Event.event_id == event.event_id).scalar()
            
            similarity = 1 - (distance if distance else 1)
            
            results.append({
                "event_id": str(event.event_id),
                "robot_id": event.robot_id,
                "user_id": event.user_id,
                "timestamp": event.timestamp,
                "source": event.source,
                "type": event.type,
                "text": event.text,
                "metadata": event.metadata,
                "score": round(similarity, 4)
            })
        
        return results
    
    def get_recent_events(
        self,
        robot_id: str,
        user_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Event]:
        """
        Get recent events for a robot/user.
        
        Args:
            robot_id: Robot identifier
            user_id: Optional user filter
            limit: Maximum results
            
        Returns:
            List of recent events
        """
        query = self.db.query(Event).filter(Event.robot_id == robot_id)
        
        if user_id:
            query = query.filter(Event.user_id == user_id)
        
        query = query.order_by(Event.timestamp.desc()).limit(limit)
        
        return query.all()

