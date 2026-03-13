"""
Voice API Endpoints
Handles voice generation and audio streaming
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from app.services.voice_service import voice_service
from typing import Optional

router = APIRouter()

@router.get("/test")
async def test_voice():
    """Test voice generation endpoint"""
    try:
        print("🧪 Testing voice generation...")
        audio_url = await voice_service.generate_voice(
            text="Hello! This is a test of the voice system.",
            character_name="suzune_horikita"
        )
        
        if audio_url:
            return {
                "status": "success",
                "message": "Voice generated successfully",
                "audio_url": audio_url
            }
        else:
            return {
                "status": "error",
                "message": "Voice generation failed"
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/{filename}")
async def get_audio(filename: str):
    """
    Stream audio file to client
    
    Args:
        filename: Name of the audio file
        
    Returns:
        Audio file stream
    """
    file_path = voice_service.get_audio_file_path(filename)
    
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=str(file_path),
        media_type="audio/wav",
        headers={
            "Cache-Control": "no-cache",
            "Accept-Ranges": "bytes"
        }
    )

@router.post("/upload")
async def upload_voice(file: UploadFile = File(...)):
    """
    Upload custom voice sample
    
    Args:
        file: Audio file (MP3, WAV, OGG, FLAC)
        
    Returns:
        Success message with character ID
    """
    try:
        print(f"📤 Receiving voice upload: {file.filename}")
        
        # Validate file type
        allowed_extensions = [".mp3", ".wav", ".ogg", ".flac"]
        file_ext = "." + file.filename.split(".")[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save the uploaded file
        character_id = await voice_service.save_custom_voice(file)
        
        print(f"✅ Voice uploaded successfully: {character_id}")
        
        return {
            "status": "success",
            "message": "Voice uploaded successfully",
            "character_id": character_id,
            "filename": file.filename
        }
        
    except Exception as e:
        print(f"❌ Error uploading voice: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-custom")
async def test_custom_voice(
    character_id: str = Form(...),
    text: str = Form(...)
):
    """
    Test custom uploaded voice
    
    Args:
        character_id: ID of the custom character
        text: Text to synthesize
        
    Returns:
        Audio URL for testing
    """
    try:
        print(f"🧪 Testing custom voice: {character_id}")
        print(f"📝 Test text: {text[:50]}...")
        
        # Generate voice with custom character
        audio_url = await voice_service.generate_voice(
            text=text,
            character_name=character_id
        )
        
        if audio_url:
            return {
                "status": "success",
                "message": "Test voice generated",
                "audio_url": audio_url
            }
        else:
            return {
                "status": "error",
                "message": "Voice generation failed"
            }
            
    except Exception as e:
        print(f"❌ Error testing voice: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/characters")
async def get_characters():
    """
    Get list of all available characters
    
    Returns:
        List of characters with their info
    """
    try:
        characters = []
        
        for char_id, char_data in voice_service.characters.items():
            # Only include non-test characters for selection
            if not char_data.get("is_test", False):
                characters.append({
                    "id": char_id,
                    "name": char_data["name"],
                    "is_custom": char_id.startswith("custom_"),
                    "is_active": voice_service.get_active_character() == char_id
                })
        
        return {
            "status": "success",
            "characters": characters,
            "active_character": voice_service.get_active_character()
        }
        
    except Exception as e:
        print(f"❌ Error getting characters: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-active-character")
async def set_active_character(character_id: str = Form(...)):
    """
    Set active character for voice generation
    
    Args:
        character_id: ID of the character to set as active
        
    Returns:
        Success message
    """
    try:
        if character_id == "suzune_horikita":
            # Reset to default
            voice_service.active_custom_character = None
            print("🔄 Reset to default voice: Suzune Horikita")
        else:
            # Set custom character as active
            success = await voice_service.set_active_custom_voice(character_id)
            if not success:
                raise HTTPException(status_code=400, detail="Character not found")
        
        return {
            "status": "success",
            "message": "Active character updated",
            "active_character": voice_service.get_active_character()
        }
        
    except Exception as e:
        print(f"❌ Error setting active character: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply-custom")
async def apply_custom_voice(
    character_id: str = Form(...),
    voice_name: str = Form(...)
):
    """
    Apply custom voice to the main character with a custom name
    
    Args:
        character_id: ID of the test character
        voice_name: User-provided name for the voice
        
    Returns:
        Success message with permanent character ID
    """
    try:
        print(f"✨ Applying custom voice: {character_id} as '{voice_name}'")
        
        # Move from testAudio to voices directory with custom name
        permanent_id = await voice_service.finalize_custom_voice(character_id, voice_name)
        
        # Set the permanent voice as active
        success = await voice_service.set_active_custom_voice(permanent_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Voice '{voice_name}' applied successfully",
                "character_id": permanent_id,
                "voice_name": voice_name
            }
        else:
            return {
                "status": "error",
                "message": "Failed to activate the voice"
            }
            
    except Exception as e:
        print(f"❌ Error applying voice: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/characters")
async def get_characters():
    """
    Get list of available characters
    
    Returns:
        List of available characters with their details
    """
    try:
        characters = voice_service.get_available_characters()
        active_character = voice_service.get_active_character()
        
        return {
            "status": "success",
            "characters": characters,
            "active_character": active_character
        }
        
    except Exception as e:
        print(f"❌ Error getting characters: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set-active-character")
async def set_active_character(character_id: str = Form(...)):
    """
    Set active character for voice generation
    
    Args:
        character_id: ID of the character to set as active
        
    Returns:
        Success message
    """
    try:
        success = await voice_service.set_active_custom_voice(character_id)
        
        if success:
            character = voice_service.characters.get(character_id)
            character_name = character["name"] if character else character_id
            
            return {
                "status": "success",
                "message": f"Active character set to {character_name}",
                "character_id": character_id,
                "character_name": character_name
            }
        else:
            return {
                "status": "error",
                "message": "Failed to set active character"
            }
            
    except Exception as e:
        print(f"❌ Error setting active character: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/character/{character_id}")
async def delete_character(character_id: str):
    """
    Delete a custom character
    
    Args:
        character_id: ID of the character to delete
        
    Returns:
        Success message
    """
    try:
        print(f"🗑️ Request to delete character: {character_id}")
        success = await voice_service.delete_custom_character(character_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Character {character_id} deleted successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to delete character (or is system character)")
            
    except Exception as e:
        print(f"❌ Error deleting character: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
