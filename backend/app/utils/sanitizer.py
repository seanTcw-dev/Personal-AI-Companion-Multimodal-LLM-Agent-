"""
Text Sanitization Utilities
"""
import re

def clean_ai_response(text: str) -> str:
    """
    Clean AI response by removing JSON blocks and internal system messages (like Event IDs).
    """
    if not text:
        return ""
        
    # Remove JSON blocks
    # Note: simple regex, catches { ... }
    text = re.sub(r'\{.*\}', '', text, flags=re.DOTALL).strip()
    
    # Remove "The event ID is..." sentences (handling potential quotes, IDs, and sentence endings)
    # Matches "The event ID is" followed by any characters until a dot or end of string
    text = re.sub(r'The event ID is .*?(\.|$)', '', text).strip()
    
    return text
