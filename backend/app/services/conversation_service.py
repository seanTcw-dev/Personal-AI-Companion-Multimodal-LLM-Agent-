"""
Conversation Service - JSON File Storage
Manages chat conversations and messages using JSON files
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class ConversationService:
    def __init__(self):
        """Initialize conversation service with JSON file storage"""
        # Use path relative to this file so it always resolves to backend/app/data/conversations
        base_dir = Path(__file__).resolve().parent.parent  # backend/app/
        self.data_dir = base_dir / "data" / "conversations"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.data_dir / "conversations_index.json"
        
        # Initialize index file if it doesn't exist
        if not self.index_file.exists():
            self._save_index({})
    
    def _load_index(self) -> Dict:
        """Load conversations index from JSON file"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_index(self, index: Dict):
        """Save conversations index to JSON file"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def _get_user_dir(self, user_id: str) -> Path:
        """Get user's conversation directory"""
        user_dir = self.data_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    def _get_conversation_path(self, user_id: str, conversation_id: str) -> Path:
        """Get path to conversation JSON file"""
        return self._get_user_dir(user_id) / f"{conversation_id}.json"
    
    def _generate_conversation_id(self, user_id: str) -> str:
        """Generate unique conversation ID"""
        index = self._load_index()
        user_convs = index.get(user_id, [])
        next_num = len(user_convs) + 1
        return f"conv_{next_num:03d}"
    
    def create_conversation(self, user_id: str, title: str = "New Chat") -> Dict:
        """Create a new conversation"""
        conv_id = self._generate_conversation_id(user_id)
        now = datetime.now().isoformat()
        
        conversation = {
            "id": conv_id,
            "user_id": user_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "messages": []
        }
        
        # Save conversation file
        conv_path = self._get_conversation_path(user_id, conv_id)
        with open(conv_path, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, indent=2, ensure_ascii=False)
        
        # Update index
        index = self._load_index()
        if user_id not in index:
            index[user_id] = []
        
        index[user_id].append({
            "id": conv_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "message_count": 0
        })
        self._save_index(index)
        
        print(f"📝 Created conversation: {conv_id} - '{title}'")
        return conversation
    
    def get_conversations(self, user_id: str) -> List[Dict]:
        """Get all conversations for a user"""
        index = self._load_index()
        return index.get(user_id, [])
    
    def get_conversation(self, user_id: str, conversation_id: str) -> Optional[Dict]:
        """Get a specific conversation with all messages"""
        conv_path = self._get_conversation_path(user_id, conversation_id)
        
        if not conv_path.exists():
            return None
        
        try:
            with open(conv_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def save_message(self, user_id: str, conversation_id: str, role: str, content: str) -> bool:
        """Add a message to a conversation"""
        conversation = self.get_conversation(user_id, conversation_id)
        
        if not conversation:
            return False
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        conversation["messages"].append(message)
        conversation["updated_at"] = datetime.now().isoformat()
        
        # Save conversation
        conv_path = self._get_conversation_path(user_id, conversation_id)
        with open(conv_path, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, indent=2, ensure_ascii=False)
        
        # Update index
        index = self._load_index()
        for conv in index.get(user_id, []):
            if conv["id"] == conversation_id:
                conv["updated_at"] = conversation["updated_at"]
                conv["message_count"] = len(conversation["messages"])
                break
        self._save_index(index)
        
        return True
    
    def rename_conversation(self, user_id: str, conversation_id: str, new_title: str) -> bool:
        """Rename a conversation"""
        conversation = self.get_conversation(user_id, conversation_id)
        
        if not conversation:
            return False
            
        # Update conversation file
        conversation["title"] = new_title
        conversation["updated_at"] = datetime.now().isoformat()
        
        conv_path = self._get_conversation_path(user_id, conversation_id)
        with open(conv_path, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, indent=2, ensure_ascii=False)
            
        # Update index
        index = self._load_index()
        for conv in index.get(user_id, []):
            if conv["id"] == conversation_id:
                conv["title"] = new_title
                conv["updated_at"] = conversation["updated_at"]
                break
        self._save_index(index)
        
        print(f"📝 Renamed conversation: {conversation_id} -> '{new_title}'")
        return True

    def delete_conversation(self, user_id: str, conversation_id: str) -> bool:
        """Delete a conversation"""
        conv_path = self._get_conversation_path(user_id, conversation_id)
        
        if not conv_path.exists():
            return False
        
        conv_path.unlink()
        
        # Update index
        index = self._load_index()
        if user_id in index:
            index[user_id] = [c for c in index[user_id] if c["id"] != conversation_id]
            self._save_index(index)
        
        print(f"🗑️ Deleted conversation: {conversation_id}")
        return True

# Create singleton instance
conversation_service = ConversationService()
