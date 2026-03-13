"""
Calendar API Endpoints
Handles Google Calendar OAuth and event management
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from app.services.calendar_service import calendar_service

# Event analysis is now handled by LLM Tools, so this endpoint is deprecated/removed.
router = APIRouter()


class EventRequest(BaseModel):
    """Request model for creating a calendar event"""
    title: str
    start_time: str  # ISO format
    end_time: str    # ISO format
    description: Optional[str] = None
    location: Optional[str] = None


class CalendarStatus(BaseModel):
    """Calendar authorization status"""
    authorized: bool
    authorization_url: Optional[str] = None

@router.post("/calendar/create-event/{user_id}")
async def create_event(user_id: str, event: EventRequest):
    """
    Create a calendar event for a user
    """
    # Check if user is authorized
    if not calendar_service.is_user_authorized(user_id):
        raise HTTPException(
            status_code=401,
            detail="User not authorized for Calendar access. Please authorize first."
        )
    
    # Create the event
    created_event = calendar_service.create_event(
        user_id=user_id,
        title=event.title,
        start_time=event.start_time,
        end_time=event.end_time,
        description=event.description,
        location=event.location
    )
    
    if not created_event:
        raise HTTPException(
            status_code=500,
            detail="Failed to create calendar event"
        )
    
    return {
        "success": True,
        "message": "Event created successfully",
        "event": created_event
    }


@router.get("/calendar/events/{user_id}")
async def list_events(user_id: str, max_results: int = Query(default=10, ge=1, le=50)):
    """
    List upcoming calendar events for a user
    """
    if not calendar_service.is_user_authorized(user_id):
        raise HTTPException(
            status_code=401,
            detail="User not authorized for Calendar access"
        )
    
    events = calendar_service.list_upcoming_events(user_id, max_results)
    
    return {
        "success": True,
        "count": len(events),
        "events": events
    }


@router.get("/calendar/oauth2callback")
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    user_id: str = Query(...)
):
    """
    OAuth2 callback endpoint for Google Calendar authorization
    
    Note: This is a simplified version. In production, you should:
    1. Store state securely and verify it
    2. Use proper session management
    3. Implement CSRF protection
    """
    try:
        # This is a placeholder - actual OAuth flow needs to be implemented
        # based on your specific requirements
        
        return {
            "success": True,
            "message": "Authorization successful. You can close this window."
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth callback error: {str(e)}"
        )
