"""
Test event parser with the user's message
"""
import sys
sys.path.append('c:/Users/SeanTeng/Desktop/Anime Model Chatbot/backend')

from app.services.event_parser import event_parser

# Test the exact message the user sent
test_message = "i have a meeting at tmr 8am"

print(f"Testing message: '{test_message}'")
print(f"\n1. Detecting event intent...")
has_intent = event_parser.detect_event_intent(test_message)
print(f"   Has event intent: {has_intent}")

print(f"\n2. Extracting event info...")
event_info = event_parser.extract_event_info(test_message)
print(f"   Event info: {event_info}")

if event_info:
    print(f"\n✅ Event detected successfully!")
    print(f"   Title: {event_info['title']}")
    print(f"   Start: {event_info['start_time']}")
    print(f"   End: {event_info['end_time']}")
else:
    print(f"\n❌ No event detected!")
    
    # Debug why
    text_lower = test_message.lower()
    print(f"\nDebug info:")
    print(f"  - Has 'meeting': {'meeting' in text_lower}")
    print(f"  - Has 'tmr': {'tmr' in text_lower}")
    print(f"  - Has 'have': {'have' in text_lower}")
    print(f"  - Has '8am': {'8am' in text_lower}")
