"""
Event Parser Service
Extracts calendar event information from natural language text
"""
import re
from datetime import datetime, timedelta
from typing import Optional, Dict

class EventParser:
    def __init__(self):
        """Initialize the Event Parser service"""
        print("📅 Event Parser Service initialized")
    
    def extract_event_info(self, text: str) -> Optional[Dict[str, str]]:
        """
        Extract event information from natural language text
        
        Args:
            text: Natural language text containing event information
            
        Returns:
            Dictionary with 'title', 'start_time', 'end_time' or None if no event detected
        """
        text_lower = text.lower()
        
        # Simple patterns to detect event creation intent
        event_keywords = [
            'remind me', 'schedule', 'meeting', 'appointment',
            'create event', 'add to calendar', 'set reminder'
        ]
        
        # Check if text contains event keywords
        has_event_keyword = any(keyword in text_lower for keyword in event_keywords)
        
        if not has_event_keyword:
            return None
        
        # Try to extract time information
        time_info = self._extract_time(text)
        if not time_info:
            return None
        
        # Extract event title
        title = self._extract_title(text)
        
        # Default 1-hour duration
        start_time = time_info
        end_time = start_time + timedelta(hours=1)
        
        return {
            'title': title,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
    
    def _extract_time(self, text: str) -> Optional[datetime]:
        """
        Extract time information from text
        Returns datetime object or None
        """
        text_lower = text.lower()
        now = datetime.now()
        
        # Check for "tomorrow" (and common abbreviations)
        if 'tomorrow' in text_lower or 'tmr' in text_lower or 'tmrw' in text_lower:
            base_time = now + timedelta(days=1)
            # Try to extract specific time
            time_match = re.search(r'(\d{1,2})\s*(am|pm|:)', text_lower)
            if time_match:
                hour = int(time_match.group(1))
                if 'pm' in text_lower and hour < 12:
                    hour += 12
                return base_time.replace(hour=hour, minute=0, second=0, microsecond=0)
            else:
                # Default to 10 AM tomorrow
                return base_time.replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Check for "today"
        if 'today' in text_lower:
            # Try to extract specific time
            time_match = re.search(r'(\d{1,2})\s*(am|pm|:)', text_lower)
            if time_match:
                hour = int(time_match.group(1))
                if 'pm' in text_lower and hour < 12:
                    hour += 12
                return now.replace(hour=hour, minute=0, second=0, microsecond=0)
            else:
                # Default to 1 hour from now
                return now + timedelta(hours=1)
        
        # Check for "in X hours/minutes"
        hours_match = re.search(r'in (\d+) hours?', text_lower)
        if hours_match:
            hours = int(hours_match.group(1))
            return now + timedelta(hours=hours)
        
        minutes_match = re.search(r'in (\d+) minutes?', text_lower)
        if minutes_match:
            minutes = int(minutes_match.group(1))
            return now + timedelta(minutes=minutes)
        
        # Check for standalone time patterns (e.g., "8am", "3pm") without "at"
        standalone_time = re.search(r'\b(\d{1,2})\s*(am|pm)\b', text_lower)
        if standalone_time:
            hour = int(standalone_time.group(1))
            am_pm = standalone_time.group(2)
            if am_pm == 'pm' and hour < 12:
                hour += 12
            elif am_pm == 'am' and hour == 12:
                hour = 0
            target_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if target_time < now:
                target_time += timedelta(days=1)
            return target_time
        
        # Check for specific time patterns (e.g., "at 3pm", "at 14:00")
        time_pattern = re.search(r'at (\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text_lower)
        if time_pattern:
            hour = int(time_pattern.group(1))
            minute = int(time_pattern.group(2)) if time_pattern.group(2) else 0
            am_pm = time_pattern.group(3)
            
            if am_pm == 'pm' and hour < 12:
                hour += 12
            elif am_pm == 'am' and hour == 12:
                hour = 0
            
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If the time has already passed today, schedule for tomorrow
            if target_time < now:
                target_time += timedelta(days=1)
            
            return target_time
        
        # Default: 1 hour from now if we detected event keywords but no specific time
        return now + timedelta(hours=1)
    
    def _extract_title(self, text: str) -> str:
        """
        Extract event title from text
        """
        # Remove common time-related phrases
        title = text
        patterns_to_remove = [
            r'remind me to\s*',
            r'schedule\s*',
            r'create an? event\s*',
            r'add to calendar\s*',
            r'set a? reminder\s*',
            r'\s*(?:tomorrow|tmrw|tmr)\s*',
            r'\s*today\s*',
            r'\s*(?:at\s+)?\d{1,2}(?::\d{2})?\s*(?:am|pm)\s*',
            r'\s*at \d{1,2}(?::\d{2})?\s*',
            r'\s*in \d+ (?:hours?|minutes?)\s*',
            r'^i have an?\s*',
            r'\s*at$'
        ]
        
        for pattern in patterns_to_remove:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Clean up and capitalize
        title = title.strip()
        if not title:
            title = "Reminder"
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        
        return title

# Create singleton instance
event_parser = EventParser()
