"""API dependencies and utilities."""
from fastapi import Header, HTTPException, status
from typing import Optional


async def verify_api_key(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify API key from Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )
    
    # Expected format: "Bearer <api_key>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format"
        )
    
    api_key = parts[1]
    
    # In production, validate against database
    # For now, accept any non-empty key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key

