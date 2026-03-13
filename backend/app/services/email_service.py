
import json
import os
import random
import uuid
from datetime import datetime
from typing import List, Dict, Optional

DATA_FILE = os.path.join(os.getcwd(), "data", "emails.json")

# Ensure data directory exists
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# Mock Data Templates - Purpose Driven
SENDERS = [
    {"name": "Project Manager", "email": "pm@company.com"},
    {"name": "HR Department", "email": "hr@company.com"},
    {"name": "IT Support", "email": "support@company.com"},
    {"name": "Client: Arasaka Corp", "email": "contact@arasaka.com"},
    {"name": "Team Lead", "email": "lead@company.com"},
    {"name": "System Monitor", "email": "alerts@internal-sys.net"}
]

TEMPLATES = [
    {
        "subject": "Urgent: Q4 Report Revision",
        "category": "Work",
        "body": "Hi,\n\nThe client requested some changes to the financial section of the Q4 report. We need this updated before the 2 PM meeting.\n\nPlease prioritize this.\n\nThanks,\nPM",
        "important": True
    },
    {
        "subject": "Meeting: Sprint Planning scheduled for 10:00 AM",
        "category": "Work",
        "body": "Team,\n\nJust a reminder that we have our sprint planning session at 10:00 AM in Conference Room B (and via Zoom).\n\nPlease review the backlog beforehand.\n\nBest,\nTeam Lead",
        "important": True
    },
    {
        "subject": "Action Required: Complete Security Training",
        "category": "Admin",
        "body": "Dear Employee,\n\nThis is a reminder to complete your mandatory cybersecurity awareness training by Friday.\n\nFailure to complete this may result in account suspension.\n\nRegards,\nHR",
        "important": False
    },
    {
        "subject": "New Task Assigned: API Integration",
        "category": "Task",
        "body": "A new task has been assigned to you in Jira: 'Integrate Payment Gateway API'.\n\nPriority: High\nDue Date: Tomorrow\n\nPlease check the dashboard for details.",
        "important": True
    },
    {
        "subject": "Server Alert: High Latency Detected",
        "category": "System",
        "body": "Warning: High latency detected on the Asia-Pacific region load balancer.\n\nResponse time > 500ms.\n\nPlease investigate immediately.",
        "important": False
    },
    {
        "subject": "Lunch & Learn: AI Ethics",
        "category": "Events",
        "body": "Join us this Friday at 12 PM for a Lunch & Learn session on 'The Ethics of AI in 2026'.\n\nPizza will be provided!\n\nRSVP by Thursday.",
        "important": False
    },
    {
        "subject": "Feedback on Design Mockups",
        "category": "Work",
        "body": "I've reviewed the latest UI mockups. The color scheme looks great, but the navigation flow feels a bit clunky on mobile.\n\nCan we discuss this afternoon?",
        "important": False
    },
    {
        "subject": "Client Meeting Rescheduled",
        "category": "Work",
        "body": "The meeting with Arasaka Corp has been moved to 3 PM due to a conflict.\n\nUpdated calendar invite attached.",
        "important": True
    }
]

class MockEmailService:
    def __init__(self):
        self._load_emails()

    def _load_emails(self):
        """Loads emails from JSON file."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.emails = json.load(f)
            except Exception:
                self.emails = []
        else:
            self.emails = []

    def _save_emails(self):
        """Saves emails to JSON file."""
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.emails, f, indent=2, ensure_ascii=False)

    def get_emails(self, limit: int = 50) -> List[Dict]:
        """Returns the list of emails, sorted by date (newest first)."""
        # Sort by timestamp descending
        sorted_emails = sorted(self.emails, key=lambda x: x['timestamp'], reverse=True)
        return sorted_emails[:limit]

    def get_unread_count(self) -> int:
        return sum(1 for e in self.emails if not e.get('read', False))

    def mark_as_read(self, email_id: str):
        for email in self.emails:
            if email['id'] == email_id:
                email['read'] = True
                self._save_emails()
                return True
        return False

    def generate_email(self) -> Dict:
        """Generates a single new mock email and saves it."""
        sender = random.choice(SENDERS)
        template = random.choice(TEMPLATES)
        
        new_email = {
            "id": str(uuid.uuid4()),
            "sender_name": sender["name"],
            "sender_email": sender["email"],
            "subject": template["subject"],
            "body": template["body"],
            "category": template["category"],
            "timestamp": datetime.now().isoformat(),
            "read": False,
            "important": template["important"] if random.random() > 0.3 else False
        }
        
        self.emails.append(new_email)
        self._save_emails()
        return new_email

    def refresh_batch(self, count: int = 3) -> List[Dict]:
        """Generates a batch of emails. Useful for 'Refresh' button."""
        new_emails = []
        for _ in range(count):
            new_emails.append(self.generate_email())
        return new_emails

email_service = MockEmailService()
