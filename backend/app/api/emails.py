"""
Email API Routes
Handles email-related endpoints (mock email service)
"""
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/emails")
async def get_emails(limit: int = Query(default=20)):
    """Get list of emails"""
    from app.services.email_service import email_service

    emails = email_service.get_emails(limit=limit)
    unread_count = email_service.get_unread_count()
    return {
        "emails": emails,
        "unread_count": unread_count
    }


@router.post("/emails/refresh")
async def refresh_emails(count: int = Query(default=3)):
    """Refresh / generate a batch of new mock emails"""
    from app.services.email_service import email_service

    new_emails = email_service.refresh_batch(count=count)
    return {
        "new_emails": new_emails,
        "message": f"Generated {len(new_emails)} new emails"
    }


@router.post("/emails/generate")
async def generate_email():
    """Generate a single new mock email"""
    from app.services.email_service import email_service

    new_email = email_service.generate_email()
    return {
        "email": new_email,
        "message": "Generated 1 new email"
    }


@router.post("/emails/{email_id}/read")
async def mark_email_read(email_id: str):
    """Mark an email as read"""
    from app.services.email_service import email_service

    success = email_service.mark_as_read(email_id)
    if success:
        return {"message": "Email marked as read"}
    return {"message": "Email not found", "error": True}
