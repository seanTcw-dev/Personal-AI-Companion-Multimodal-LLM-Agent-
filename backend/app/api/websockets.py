from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
import json
import re
import os
from datetime import datetime, timedelta
from app.services.ollama_service import ollama_service
from app.services.voice_service import voice_service
from app.services.calendar_service import calendar_service
from app.services.ai_service import ai_service

print(f"🤖 Using Ollama AI service (with AI-driven tool calling)")


class ConnectionManager:
    def __init__(self):
        # Map user_id -> list of active WebSocket connections
        self.user_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        # Accept the WebSocket connection
        await websocket.accept()
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)
        print(f"📡 User {user_id} now has {len(self.user_connections[user_id])} connection(s)")

    def disconnect(self, websocket: WebSocket, user_id: str):
        # Remove the WebSocket from the user's connections
        if user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        # Send a message to a specific client
        await websocket.send_text(message)

    async def send_personal_json(self, data: Dict[str, Any], websocket: WebSocket):
        # Send a JSON message to a specific client
        await websocket.send_json(data)

    async def broadcast_to_user(self, data: Dict[str, Any], user_id: str, exclude: WebSocket = None):
        """Send JSON to ALL connections for a user, optionally excluding one."""
        if user_id not in self.user_connections:
            return
        stale = []
        for ws in self.user_connections[user_id]:
            if ws == exclude:
                continue
            try:
                await ws.send_json(data)
            except Exception:
                stale.append(ws)
        for ws in stale:
            if ws in self.user_connections.get(user_id, []):
                self.user_connections[user_id].remove(ws)

    async def broadcast_status(self, status: str, detail: str, user_id: str):
        """Send a status update to ALL connections for a user."""
        await self.broadcast_to_user({
            "type": "status",
            "status": status,
            "detail": detail
        }, user_id)


# Create a singleton instance of the connection manager
manager = ConnectionManager()


async def execute_tool(tool_name: str, params: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
    """
    Execute a tool call and return the result.
    This is the WebSocket-side tool executor that handles all tool types.
    """
    print(f"🔧 Executing tool: {tool_name} with params: {params}")
    
    if tool_name == "create_calendar_event":
        title = params.get("title", "Untitled Event")
        start_time = params.get("start_time", "")
        end_time = params.get("end_time", "")
        description = params.get("description", "")
        
        # Calculate end_time if missing (default 1 hour)
        if not end_time and start_time:
            try:
                start_dt = datetime.fromisoformat(start_time)
                end_dt = start_dt + timedelta(hours=1)
                end_time = end_dt.isoformat()
            except Exception:
                end_time = start_time
        
        # Check authorization
        if not calendar_service.is_user_authorized(user_id):
            print(f"⚠️ User {user_id} not authorized for Calendar")
            return {"tool": tool_name, "error": "User not authorized for Google Calendar. Please authorize first."}
        
        # Create the event
        result = calendar_service.create_event(
            user_id=user_id,
            title=title,
            start_time=start_time,
            end_time=end_time or start_time,
            description=description or f"Created via AI assistant"
        )
        
        if result:
            print(f"✅ Calendar event created: {result.get('title')} at {result.get('start')}")
            return {"tool": tool_name, "success": True, "event": result}
        else:
            return {"tool": tool_name, "error": "Failed to create calendar event"}
    
    elif tool_name == "open_url":
        # URL opening is handled client-side, just pass it through
        return {"tool": tool_name, "action": "open_url", "params": params}
    
    elif tool_name in ("create_file", "read_file", "edit_file"):
        # File operations
        sandbox_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "user_files")
        os.makedirs(sandbox_dir, exist_ok=True)
        
        filename = params.get("filename", "")
        if ".." in filename or "/" in filename or "\\" in filename:
            return {"tool": tool_name, "error": "Invalid filename"}
        
        file_path = os.path.join(sandbox_dir, filename)
        
        if tool_name == "create_file":
            content = params.get("content", "")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"tool": tool_name, "success": True, "message": f"File '{filename}' created"}
        
        elif tool_name == "read_file":
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                return {"tool": tool_name, "success": True, "content": content, "filename": filename}
            else:
                return {"tool": tool_name, "error": f"File '{filename}' not found"}
        
        elif tool_name == "edit_file":
            content = params.get("content", "")
            if os.path.exists(file_path):
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write("\n" + content)
                return {"tool": tool_name, "success": True, "message": f"Content appended to '{filename}'"}
            else:
                return {"tool": tool_name, "error": f"File '{filename}' not found"}
    
    else:
        return {"tool": tool_name, "error": f"Unknown tool: {tool_name}"}


def build_tool_result_context(tool_result: Dict[str, Any]) -> str:
    """Build a system context string from tool execution result for AI to respond naturally."""
    tool_name = tool_result.get("tool", "unknown")
    
    if tool_result.get("error"):
        return (
            f"[SYSTEM: Tool '{tool_name}' FAILED. Error: {tool_result['error']}. "
            f"Please inform the user about this issue naturally.]"
        )
    
    if tool_name == "create_calendar_event":
        event = tool_result.get("event", {})
        return (
            f"[SYSTEM: A Google Calendar event was SUCCESSFULLY created. "
            f"Title: '{event.get('title', 'Event')}', "
            f"Time: {event.get('start', 'N/A')}. "
            f"Please confirm this to the user naturally. Do not mention the link.]"
        )
    
    if tool_name in ("create_file", "edit_file"):
        return f"[SYSTEM: {tool_result.get('message', 'File operation completed')}. Confirm to the user naturally.]"
    
    if tool_name == "read_file":
        content = tool_result.get("content", "")
        filename = tool_result.get("filename", "file")
        return f"[SYSTEM: Content of '{filename}':\n{content}\n\nSummarize or present this to the user naturally.]"
    
    return f"[SYSTEM: Tool '{tool_name}' executed successfully. Confirm to the user.]"


async def send_status(websocket: WebSocket, status: str, detail: str = "", user_id: str = None):
    """Send a status update to all connections for the user (or just one)."""
    if user_id:
        await manager.broadcast_status(status, detail, user_id)
    else:
        await websocket.send_json({
            "type": "status",
            "status": status,
            "detail": detail
        })


async def process_and_stream(
    message_text: str,
    user_id: str,
    websocket: WebSocket,
    active_character: str
):
    """
    Process a user message with AI-driven tool detection and streaming response.
    
    Flow:
    1. AI intent detection → decide if a tool is needed
    2. If TOOL → AI generates tool JSON → execute tool → stream confirmation
    3. If CHAT → stream response directly
    """
    system_context = None
    tool_result = None
    
    # Step 1: AI-driven intent detection (let AI decide, not hardcoded regex)
    print(f"🧠 AI routing message: '{message_text[:60]}...'")
    await send_status(websocket, "thinking", "Analyzing your message...", user_id)
    relevant_tool = await ai_service._decide_intent(message_text)
    
    if relevant_tool:
        print(f"🔧 AI detected tool intent: {relevant_tool['name']}")
        await send_status(websocket, "tool_calling", f"Using tool: {relevant_tool['name']}", user_id)
        
        # Step 2: Ask AI to generate tool call JSON
        tools_json = json.dumps(relevant_tool['tools'], indent=2)
        tool_prompt_context = (
            f"### IMPORTANT: TOOL MANUAL ACTIVATED: {relevant_tool['name']}\n"
            f"User Intent: {message_text}\n"
            f"You MUST use the following tools to fulfill this request:\n"
            f"{tools_json}\n\n"
            f"CRITICAL INSTRUCTIONS:\n"
            f"1. OUTPUT VALID JSON ONLY. Do not write any introduction or conclusion.\n"
            f"2. Format: {{ \"tool\": \"tool_name\", \"parameters\": {{ ... }} }}\n"
            f"3. For dates: Current date is {datetime.now().strftime('%Y-%m-%d')}. "
            f"'tomorrow'/'tmr' = {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}. "
            f"Use ISO 8601 format for times.\n"
            f"4. Extract a CLEAN title from the user's message (remove greetings, filler words).\n"
        )
        
        # Generate tool JSON (non-streaming, forced JSON mode)
        tool_response = await ollama_service.generate_response(
            user_message=message_text,
            user_id=user_id,
            system_context=tool_prompt_context,
            add_to_history=False,  # Don't save tool generation to history
            format='json',
            temperature=0.0
        )
        
        tool_json_text = tool_response.get('text', '') if tool_response else ''
        if not tool_json_text:
            tool_json_text = ''
        print(f"🤖 AI tool JSON: {tool_json_text}")
        
        # Step 3: Parse and execute the tool
        try:
            # Find JSON in response
            json_match = re.search(r'\{.*\}', tool_json_text, re.DOTALL)
            if json_match:
                tool_data = json.loads(json_match.group(0))
                tool_name = tool_data.get("tool", "")
                params = tool_data.get("parameters", {})
                
                if tool_name:
                    await send_status(websocket, "tool_executing", f"Executing: {tool_name}", user_id)
                    tool_result = await execute_tool(tool_name, params, user_id)
                    if tool_result is not None:
                        system_context = build_tool_result_context(tool_result)
                    print(f"✅ Tool executed. Context: {(system_context or '')[:80]}...")
                else:
                    print(f"⚠️ AI generated JSON but no 'tool' field found")
            else:
                print(f"⚠️ AI failed to generate valid tool JSON")
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️ Failed to parse tool JSON: {e}")
            # Fall through to normal chat
    else:
        print(f"🗣️ AI decided: CHAT mode (no tool needed)")
    
    # Step 4: Stream the natural language response (with or without tool context)
    print(f"🌊 Starting sentence-level streaming...")
    await send_status(websocket, "generating", "Generating response...", user_id)
    full_response_text = ""
    full_response_emotion = "neutral"
    sentence_index = 0
    
    async for chunk in ollama_service.generate_response_streaming(message_text, user_id, system_context):
        sentence = chunk.get("sentence", "")
        is_final = chunk.get("is_final", False)
        
        if is_final:
            full_response_text = chunk.get("full_text", full_response_text)
            full_response_emotion = chunk.get("emotion", full_response_emotion)
            
            print(f"✅ Streaming complete. Final text: {full_response_text[:100]}...")
            print(f"📤 Sending FINAL message to frontend")
            
            final_response = {
                "text": full_response_text,
                "emotion": full_response_emotion,
                "conversation_id": chunk.get("conversation_id"),
                "conversation_title": chunk.get("conversation_title"),
                "is_final": True,
                "streaming": True
            }
            
            # Attach tool result if available (e.g. calendar event for frontend display)
            if tool_result and tool_result.get("success"):
                if tool_result.get("tool") == "create_calendar_event":
                    final_response['calendar_event'] = tool_result.get("event")
                elif tool_result.get("action") == "open_url":
                    final_response['open_url'] = tool_result.get("params", {})
            
            # Send final to originating connection
            await manager.send_personal_json(final_response, websocket)
            # Broadcast to OTHER connections (no audio duplication needed for final)
            await manager.broadcast_to_user(final_response, user_id, exclude=websocket)
            await send_status(websocket, "idle", "", user_id)
            print(f"✅ Final message broadcast to all connections for {user_id}")
            break
        
        if sentence:
            sentence_index += 1
            print(f"🎤 Generating voice for sentence {sentence_index}: {sentence[:50]}...")
            await send_status(websocket, "voice", f"Generating voice ({sentence_index})...", user_id)
            
            # Generate voice for this sentence IMMEDIATELY
            audio_url = await voice_service.generate_voice(
                text=sentence,
                character_name=active_character
            )
            
            # Send sentence with audio immediately
            sentence_response = {
                "text": sentence,
                "emotion": chunk.get("emotion", "neutral"),
                "audio_url": audio_url,
                "sentence_index": sentence_index,
                "is_final": False,
                "streaming": True,
                "conversation_id": chunk.get("conversation_id"),
                "conversation_title": chunk.get("conversation_title")
            }
            
            # Send WITH audio to originating connection only
            await manager.send_personal_json(sentence_response, websocket)
            
            # Broadcast to OTHER connections WITHOUT audio (prevent duplicate playback)
            sentence_no_audio = {k: v for k, v in sentence_response.items() if k != 'audio_url'}
            await manager.broadcast_to_user(sentence_no_audio, user_id, exclude=websocket)
            
            if audio_url:
                print(f"✅ Sentence {sentence_index} sent with audio: {audio_url}")
            else:
                print(f"⚠️ Sentence {sentence_index} sent without audio")
            
            full_response_text += sentence + " "


# WebSocket endpoint for chat
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    print(f"✅ User {user_id} connected to WebSocket")
    
    # Clear active conversation on new connection (e.g. page refresh)
    # This ensures "New Chat" state is synced with backend
    ollama_service.clear_active_conversation(user_id)
    
    try:
        while True:
            # Receive a message from the client
            data = await websocket.receive_text()
            
            try:
                # Try to parse the message as JSON
                message_data = json.loads(data)
                
                # Handle restore conversation request (after stop/reconnect)
                if message_data.get("type") == "restore_conversation":
                    conv_id = message_data.get("conversation_id")
                    if conv_id:
                        ollama_service.active_conversations[user_id] = conv_id
                        print(f"🔄 Restored active conversation for {user_id}: {conv_id}")
                    continue
                
                # Handle conversation created notification (for soft sync)
                if message_data.get("type") == "conversation_created":
                    conv_id = message_data.get("conversation_id")
                    conv_title = message_data.get("conversation_title", "New Chat")
                    source = message_data.get("source", "unknown")
                    
                    print(f"📢 Broadcasting conversation_created from {source}: {conv_id}")
                    
                    # Broadcast to OTHER connections (not the sender)
                    await manager.broadcast_to_user({
                        "type": "conversation_created",
                        "conversation_id": conv_id,
                        "conversation_title": conv_title,
                        "source": source
                    }, user_id, exclude=websocket)
                    continue
                
                message_text = message_data.get("text", "")
                is_hidden = message_data.get("hidden", False)
                
                print(f"📨 Received from {user_id}: {message_text}")
                if is_hidden:
                    print(f"🔒 Hidden message (won't appear in chat UI)")
                
                # Echo user message to OTHER connections (e.g. web sees desktop pet msgs)
                if not is_hidden:
                    # Include conversation_id so the Web UI can filter out messages
                    # from Desktop Pet that belong to a different conversation
                    echo_conv_id = ollama_service.active_conversations.get(user_id)
                    await manager.broadcast_to_user({
                        "type": "user_message_echo",
                        "text": message_text,
                        "conversation_id": echo_conv_id
                    }, user_id, exclude=websocket)
                
                # Get active character for voice
                active_character = voice_service.get_active_character()
                print(f"🎭 Using character: {active_character}")
                
                # Process with AI-driven tool calling and streaming
                await process_and_stream(message_text, user_id, websocket, active_character)
            
            except json.JSONDecodeError:
                # If not valid JSON, treat as plain text
                print(f"📨 Received plain text from {user_id}: {data}")
                
                active_character = voice_service.get_active_character()
                
                # Process with AI-driven tool calling and streaming
                await process_and_stream(data, user_id, websocket, active_character)
            
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                import traceback
                traceback.print_exc()
                # Send error response
                await manager.send_personal_json({
                    "text": "I apologize, but I encountered an error. Please try again.",
                    "emotion": "neutral"
                }, websocket)
    
    except WebSocketDisconnect:
        # Handle client disconnection
        manager.disconnect(websocket, user_id)
        print(f"❌ User {user_id} disconnected from WebSocket")