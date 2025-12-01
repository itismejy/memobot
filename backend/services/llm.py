"""LLM service for generating answers and summaries."""
from typing import List, Dict, Any, Optional
from backend.config import get_settings

settings = get_settings()


class LLMService:
    """Service for LLM-powered operations."""
    
    def __init__(self):
        """Initialize LLM service."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_api_key)
            print("Initialized OpenAI LLM service")
        except Exception as e:
            print(f"Failed to initialize OpenAI: {e}")
            self.client = None
    
    def generate_answer(
        self,
        question: str,
        events: List[Dict[str, Any]],
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Generate an answer based on events.
        
        Args:
            question: User question
            events: Retrieved relevant events
            max_tokens: Maximum response tokens
            
        Returns:
            Dict with answer, confidence, and supporting events
        """
        if not self.client or not events:
            return {
                "answer": "I don't have enough information to answer that question.",
                "confidence": 0.0,
                "supporting_events": []
            }
        
        # Build context from events
        context_parts = []
        for i, event in enumerate(events[:10], 1):  # Limit to top 10
            text = event.get("text", "")
            timestamp = event.get("timestamp", "")
            event_type = event.get("type", "")
            
            if text:
                context_parts.append(f"{i}. [{timestamp}] {event_type}: {text}")
        
        context = "\n".join(context_parts)
        
        # Create prompt
        prompt = f"""Based on the following events from a robot's memory, answer the user's question.

Events:
{context}

Question: {question}

Provide a concise, factual answer based only on the information in the events. If the events don't contain enough information, say so. Also rate your confidence from 0.0 to 1.0."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on robot memory events. Be concise and factual."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Extract confidence (simple heuristic based on events)
            confidence = min(0.9, len(events) / 10.0 * 0.9) if events else 0.1
            
            # Select supporting events (top 3)
            supporting = [
                {
                    "event_id": str(e.get("event_id", "")),
                    "timestamp": e.get("timestamp"),
                    "text": e.get("text")
                }
                for e in events[:3]
            ]
            
            return {
                "answer": answer,
                "confidence": round(confidence, 2),
                "supporting_events": supporting
            }
        
        except Exception as e:
            print(f"LLM error: {e}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "confidence": 0.0,
                "supporting_events": []
            }
    
    def summarize_session(self, events: List[Dict[str, Any]]) -> str:
        """
        Generate a summary of a session from events.
        
        Args:
            events: List of events in the session
            
        Returns:
            Summary text
        """
        if not self.client or not events:
            return "No events to summarize."
        
        # Build event list
        event_texts = []
        for event in events:
            text = event.get("text", "")
            event_type = event.get("type", "")
            if text:
                event_texts.append(f"{event_type}: {text}")
        
        context = "\n".join(event_texts[:50])  # Limit context
        
        prompt = f"""Summarize the following interaction between a robot and user in 2-3 sentences:

{context}

Focus on key topics discussed and any preferences or requests mentioned."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes robot interactions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"Summarization error: {e}")
            return "Error generating summary."
    
    def extract_facts(self, events: List[Dict[str, Any]], entity_id: str) -> List[Dict[str, Any]]:
        """
        Extract facts from events about an entity.
        
        Args:
            events: List of events
            entity_id: Entity identifier
            
        Returns:
            List of facts as {subject, predicate, object, confidence}
        """
        if not self.client or not events:
            return []
        
        # Build context
        event_texts = [e.get("text", "") for e in events if e.get("text")]
        context = "\n".join(event_texts[:20])
        
        prompt = f"""Extract factual statements about entity "{entity_id}" from these events:

{context}

Format each fact as: subject | predicate | object
Example: user-123 | prefers | tea
Only extract clear, factual statements."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You extract structured facts from text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.2
            )
            
            # Parse facts
            facts = []
            for line in response.choices[0].message.content.strip().split("\n"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 3:
                    facts.append({
                        "subject": parts[0],
                        "predicate": parts[1],
                        "object": parts[2],
                        "confidence": 0.8  # Default confidence
                    })
            
            return facts
        
        except Exception as e:
            print(f"Fact extraction error: {e}")
            return []


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

