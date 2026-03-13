"""
Conversations API
REST endpoints for managing chat conversations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.conversation_service import conversation_service

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

# Request/Response Models
class CreateConversationRequest(BaseModel):
    user_id: str = "user_default"
    title: str = "New Chat"

class UpdateConversationRequest(BaseModel):
    title: str

@router.patch("/{conversation_id}")
async def rename_conversation(conversation_id: str, request: UpdateConversationRequest, user_id: str = "user_default"):
    """Rename a conversation"""
    try:
        success = conversation_service.rename_conversation(
            user_id=user_id,
            conversation_id=conversation_id,
            new_title=request.title
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "success": True,
            "message": "Conversation renamed successfully",
            "title": request.title
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation"""
    try:
        conversation = conversation_service.create_conversation(
            user_id=request.user_id,
            title=request.title
        )
        return {
            "success": True,
            "conversation": conversation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_conversations(user_id: str = "user_default"):
    """Get all conversations for a user"""
    try:
        conversations = conversation_service.get_conversations(user_id)
        return {
            "success": True,
            "conversations": conversations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str, user_id: str = "user_default"):
    """Get a specific conversation with messages"""
    try:
        conversation = conversation_service.get_conversation(user_id, conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "success": True,
            "conversation": conversation
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, user_id: str = "user_default"):
    """Delete a conversation"""
    try:
        success = conversation_service.delete_conversation(user_id, conversation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "success": True,
            "message": "Conversation deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{conversation_id}/activate")
async def activate_conversation(conversation_id: str, user_id: str = "user_default"):
    """Set a conversation as active for the user"""
    try:
        from app.services.ollama_service import ollama_service
        
        # Verify conversation exists
        conversation = conversation_service.get_conversation(user_id, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Set as active in ollama service
        ollama_service.active_conversations[user_id] = conversation_id
        
        return {
            "success": True,
            "message": f"Conversation {conversation_id} is now active"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
