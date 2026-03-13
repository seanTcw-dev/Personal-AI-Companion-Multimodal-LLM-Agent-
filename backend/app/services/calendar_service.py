"""
Google Calendar Service
Handles Google Calendar API integration for creating and managing events
"""
import os
import pickle
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()


class CalendarService:
    def __init__(self):
        """Initialize the Calendar Service"""
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.credentials_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'credentials')
        self.token_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'calendar_tokens')
        
        # Load OAuth credentials from environment
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        # Create directories if they don't exist
        os.makedirs(self.credentials_dir, exist_ok=True)
        os.makedirs(self.token_dir, exist_ok=True)
        
        # User credentials cache (user_id -> Credentials)
        self.user_credentials: Dict[str, Credentials] = {}
        
        print(f"📅 Google Calendar Service initialized")
        print(f"📁 Token directory: {self.token_dir}")
    
    def get_user_token_path(self, user_id: str) -> str:
        """Get the path to a user's token file"""
        return os.path.join(self.token_dir, f'calendar_token_{user_id}.pickle')
    
    def load_user_credentials(self, user_id: str) -> Optional[Credentials]:
        """Load saved credentials for a user"""
        token_path = self.get_user_token_path(user_id)
        
        if os.path.exists(token_path):
            try:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
                    
                    # Check if credentials are valid
                    if creds and creds.valid:
                        self.user_credentials[user_id] = creds
                        return creds
                    
                    # Refresh if expired
                    if creds and creds.expired and creds.refresh_token:
                        from google.auth.transport.requests import Request
                        creds.refresh(Request())
                        self.save_user_credentials(user_id, creds)
                        self.user_credentials[user_id] = creds
                        return creds
            except Exception as e:
                print(f"⚠️ Error loading credentials for user {user_id}: {e}")
        
        return None
    
    def save_user_credentials(self, user_id: str, credentials: Credentials):
        """Save user credentials to file"""
        token_path = self.get_user_token_path(user_id)
        with open(token_path, 'wb') as token_file:
            pickle.dump(credentials, token_file)
        print(f"📁 Saved credentials for user {user_id}")
    
    def store_user_tokens(self, user_id: str, access_token: str, refresh_token: Optional[str], token_data: Dict):
        """
        Store user tokens from OAuth code exchange
        
        Args:
            user_id: User identifier (Google sub)
            access_token: OAuth access token
            refresh_token: OAuth refresh token (optional)
            token_data: Full token response from Google
        """
        try:
            # Create Credentials object from token data
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.SCOPES
            )
            
            # Save credentials to file
            self.save_user_credentials(user_id, credentials)
            print(f"✅ Stored Calendar tokens for user {user_id}")
            
        except Exception as e:
            print(f"❌ Error storing tokens for user {user_id}: {e}")
            raise
    
    def is_user_authorized(self, user_id: str) -> bool:
        """Check if a user has valid Calendar credentials"""
        credentials = self.load_user_credentials(user_id)
        return credentials is not None and credentials.valid
    
    def get_authorization_url(self, user_id: str) -> str:
        """
        Generate OAuth authorization URL for a user
        
        Returns:
            Authorization URL to redirect user to
        """
        client_secrets_file = os.path.join(
            self.credentials_dir, 
            'client_secret.json'
        )
        
        if not os.path.exists(client_secrets_file):
            # Try looking in backend folder
            client_secrets_file = os.path.join(
                os.path.dirname(__file__), '..', '..', 
                'client_secret_321691644457-blm788i9mv5jt9qnh0fq93aa7qf4eigu.apps.googleusercontent.com.json'
            )
        
        if not os.path.exists(client_secrets_file):
            raise FileNotFoundError(
                "Google Calendar client secrets file not found. "
                "Please download it from Google Cloud Console and save it."
            )
        
        flow = Flow.from_client_secrets_file(
            client_secrets_file,
            scopes=self.SCOPES,
            redirect_uri=os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/api/calendar/oauth2callback')
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Save state for verification
        state_path = os.path.join(self.token_dir, f'state_{user_id}.txt')
        with open(state_path, 'w') as f:
            f.write(state)
        
        return authorization_url
    
    def create_event(
        self, 
        user_id: str, 
        title: str, 
        start_time: str, 
        end_time: str,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create a calendar event for a user
        
        Args:
            user_id: User identifier
            title: Event title
            start_time: ISO format start time
            end_time: ISO format end time
            description: Optional event description
            location: Optional event location
            
        Returns:
            Event details or None if failed
        """
        # Load user credentials
        creds = self.load_user_credentials(user_id)
        if not creds:
            print(f"❌ No credentials found for user {user_id}")
            return None
        
        try:
            # Build Calendar API service
            service = build('calendar', 'v3', credentials=creds)
            
            # Parse datetime strings
            # If string ends with 'Z', it's UTC. If not, treat as local time but ensure ISO format
            if start_time.endswith('Z'):
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            else:
                start_dt = datetime.fromisoformat(start_time)
                
            if end_time.endswith('Z'):
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            else:
                end_dt = datetime.fromisoformat(end_time)
            
            # Create event object
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_dt.isoformat(),
                    'timeZone': 'Asia/Kuala_Lumpur',  # Use user's local timezone (UTC+8)
                },
                'end': {
                    'dateTime': end_dt.isoformat(),
                    'timeZone': 'Asia/Kuala_Lumpur',
                },
            }
            
            if description:
                event['description'] = description
            
            if location:
                event['location'] = location
            
            # Create the event
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            print(f"✅ Event created successfully")
            
            return {
                'id': created_event.get('id'),
                'title': created_event.get('summary'),
                # 'link': created_event.get('htmlLink'), # Hidden per user request
                'start': created_event['start'].get('dateTime'),
                'end': created_event['end'].get('dateTime')
            }
        
        except HttpError as error:
            print(f"❌ Calendar API error: {error}")
            return None
            
        except Exception as e:
            print(f"❌ Error creating event: {e}")
            return None
    
    def list_upcoming_events(self, user_id: str, max_results: int = 10) -> List[Dict]:
        """
        List upcoming events for a user
        
        Args:
            user_id: User identifier
            max_results: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        creds = self.load_user_credentials(user_id)
        if not creds:
            return []
        
        try:
            service = build('calendar', 'v3', credentials=creds)
            
            # Get events starting from now
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return [
                {
                    'id': event.get('id'),
                    'title': event.get('summary'),
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date')),
                    'link': event.get('htmlLink')
                }
                for event in events
            ]
        
        except HttpError as error:
            print(f"❌ Error listing events: {error}")
            return []


# Create singleton instance
calendar_service = CalendarService()
