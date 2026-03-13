from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow
import os
import httpx
from dotenv import load_dotenv
from app.services.calendar_service import calendar_service

load_dotenv()

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/calendar/oauth2callback")

class GoogleTokenRequest(BaseModel):
    credential: str

class GoogleCodeRequest(BaseModel):
    code: str

class UserInfo(BaseModel):
    email: str
    name: str
    picture: str
    sub: str  # Google User ID
    calendar_authorized: bool = False

@router.post("/auth/google/verify", response_model=UserInfo)
async def verify_google_token(token_request: GoogleTokenRequest):
    """
    Verify Google OAuth token and return user information
    """
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token_request.credential, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Token is valid, return user info
        return UserInfo(
            email=idinfo['email'],
            name=idinfo.get('name', ''),
            picture=idinfo.get('picture', ''),
            sub=idinfo['sub']
        )
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=401, 
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error verifying token: {str(e)}"
        )

@router.post("/auth/google/exchange")
async def exchange_google_code(code_request: GoogleCodeRequest):
    """
    Exchange Google OAuth authorization code for tokens and user info
    This endpoint handles the unified OAuth flow with Calendar scope
    """
    try:
        # Exchange authorization code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                token_url,
                data={
                    "code": code_request.code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": "postmessage",  # For popup flow
                    "grant_type": "authorization_code"
                }
            )
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to exchange code: {token_response.text}"
            )
        
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        id_token_str = tokens.get("id_token")
        
        # Verify ID token and get user info
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )
        
        user_id = idinfo['sub']
        
        # Store Calendar tokens in calendar_service
        if access_token:
            calendar_service.store_user_tokens(
                user_id=user_id,
                access_token=access_token,
                refresh_token=refresh_token,
                token_data=tokens
            )
            print(f"✅ Stored Calendar tokens for user {user_id}")
        
        # Return user info with Calendar authorization status
        return UserInfo(
            email=idinfo['email'],
            name=idinfo.get('name', ''),
            picture=idinfo.get('picture', ''),
            sub=user_id,
            calendar_authorized=bool(access_token)
        )
    
    except Exception as e:
        print(f"❌ Error exchanging code: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error exchanging authorization code: {str(e)}"
        )

@router.get("/auth/status")
async def auth_status():
    """
    Check if Google OAuth is properly configured
    """
    return {
        "google_oauth_enabled": bool(GOOGLE_CLIENT_ID),
        "client_id_configured": bool(GOOGLE_CLIENT_ID)
    }


@router.get("/auth/desktop-user")
async def get_desktop_user():
    """
    Return the most recently logged-in user ID for the desktop pet.
    Scans calendar token files and returns the user with the most recent token file.
    This allows the desktop pet (which has no Google login UI)
    to connect as the same user as the web app.
    """
    token_dir = calendar_service.token_dir
    most_recent_user = None
    most_recent_time = 0
    
    if os.path.isdir(token_dir):
        for filename in os.listdir(token_dir):
            if filename.startswith("calendar_token_") and filename.endswith(".pickle"):
                user_id = filename.replace("calendar_token_", "").replace(".pickle", "")
                if user_id:
                    # Get file modification time
                    file_path = os.path.join(token_dir, filename)
                    mtime = os.path.getmtime(file_path)
                    if mtime > most_recent_time:
                        most_recent_time = mtime
                        most_recent_user = user_id
    
    if most_recent_user:
        print(f"🔐 Desktop Pet using most recent user: {most_recent_user}")
        return {"user_id": most_recent_user}
    
    print("⚠️ No users found, using default")
    return {"user_id": "user_default"}

# Alias endpoint for consistency
@router.get("/auth/current-user")
async def get_current_user():
    """Alias for /auth/desktop-user for consistency"""
    return await get_desktop_user()

