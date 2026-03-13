"""
Ollama Local AI Service
Handles conversation with local Ollama models running in WSL
"""
import os
import re
import asyncio
import ollama
from typing import Any, Dict, List, Literal, Optional, AsyncGenerator, Union
from dotenv import load_dotenv
from app.config.character_config import (
    PRESET_RESPONSES, PERSONALITY_PROMPT, PRESET_PATTERNS,
    EMOTION_KEYWORDS, MAX_HISTORY_MESSAGES, CONTEXT_WINDOW
)
from app.services.conversation_service import conversation_service

# Load environment variables
load_dotenv()

class OllamaService:
    def __init__(self):
        """Initialize the Ollama AI service"""
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct-q6_k")
        
        # Configure Ollama client
        self.client = ollama.Client(host=self.base_url)
        
        print(f"🤖 Using Ollama model: {self.model_name}")
        print(f"🔗 Ollama URL: {self.base_url}")
        
        # Active conversations for context (user_id -> conversation_id)
        self.active_conversations: Dict[str, str] = {}
        
        # Load preset responses from config
        self.preset_responses = PRESET_RESPONSES
        self.preset_patterns = PRESET_PATTERNS
        
        # System prompt for Suzune Horikita's personality
        self.system_prompt = PERSONALITY_PROMPT

    def clear_active_conversation(self, user_id: str):
        """Clear the active conversation for a user, forcing a new one next time"""
        if user_id in self.active_conversations:
            del self.active_conversations[user_id]
            print(f"🧹 Cleared active conversation for user {user_id}")

    def get_or_create_conversation(self, user_id: str, first_message: Optional[str] = None) -> str:
        """Get active conversation ID or create new one"""
        if user_id not in self.active_conversations:
            # Create a new conversation with title from first message
            title = "New Chat"
            if first_message:
                # Use first 50 chars of message as title
                title = first_message[:50] + ("..." if len(first_message) > 50 else "")
            
            conv = conversation_service.create_conversation(user_id, title)
            self.active_conversations[user_id] = conv["id"]
            print(f"📝 Auto-created conversation: {conv['id']} - '{title}'")
        return self.active_conversations[user_id]
    
    async def generate_title(self, text: str) -> str:
        """Generate a short title for the conversation using AI"""
        try:
            # Create a simple prompt for summarization
            # We want a very short title (3-5 words)
            prompt = f"Summarize the following message into a short, concise title (max 5 words). Do not include quotes. Message: {text}"
            
            response = await asyncio.to_thread(
                self.client.generate,
                model=self.model_name,
                prompt=prompt,
                stream=False  # Keep False for title generation (needs full response)
            )
            
            title = response['response'].strip().replace('"', '').replace("'", "")
            print(f"🧠 Generated title: '{title}'")
            return title
            
        except Exception as e:
            print(f"⚠️ Failed to generate title: {e}")
            # Fallback to truncation
            return text[:30].strip() + ("..." if len(text) > 30 else "")

    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """Get conversation history from persistent storage"""
        # Don't auto-create here, just return empty if no conversation
        if user_id not in self.active_conversations:
            return []
        
        conv_id = self.active_conversations[user_id]
        conversation = conversation_service.get_conversation(user_id, conv_id)
        
        if conversation and "messages" in conversation:
            return conversation["messages"]
        return []

    async def add_to_history(self, user_id: str, role: str, content: str):
        """Add message to conversation history (persistent storage)"""
        # Auto-create conversation if needed, using first message as title
        if role == "user":
            conv_id = self.get_or_create_conversation(user_id, content)
            
            # Check if we should rename "New Chat"
            try:
                conversation = conversation_service.get_conversation(user_id, conv_id)
                if conversation and conversation.get("title") == "New Chat":
                    # Generate a better title from user message using AI
                    new_title = await self.generate_title(content)
                    conversation_service.rename_conversation(user_id, conv_id, new_title)
            except Exception as e:
                print(f"⚠️ Failed to auto-rename conversation: {e}")
        else:
            conv_id = self.get_or_create_conversation(user_id)
        
        conversation_service.save_message(user_id, conv_id, role, content)

    def check_preset_response(self, user_message: str) -> Optional[str]:
        """Check if the user message matches a preset response pattern"""
        message_lower = user_message.lower().strip()
        
        # Remove common punctuation
        message_clean = message_lower.rstrip('?!.,')
        
        # Check each preset pattern category
        for response_key, patterns in self.preset_patterns.items():
            if any(pattern in message_clean for pattern in patterns):
                return self.preset_responses.get(response_key)
        
        return None

    async def generate_response(self, user_message: str, user_id: str, system_context: Optional[str] = None, add_to_history: bool = True, format: Optional[Literal['', 'json']] = None, temperature: Optional[float] = None, role: str = "user") -> Dict[str, Optional[str]]:
        """
        Generate AI response using Ollama
        
        Args:
            user_message: The user's input message
            user_id: Unique identifier for the user
            system_context: Optional temporary context to inject (not saved to history)
            add_to_history: Whether to save the user message to conversation history
            format: Optional format for the response (e.g. 'json')
            temperature: Optional temperature for the model (0.0 to 1.0)
            role: Role of the message sender (default: "user", can be "system")
            
        Returns:
            Dictionary with 'text', 'emotion', 'conversation_id', and 'conversation_title' keys
        """
        # Check for preset responses first, BUT skip if:
        # 1. We have system context (e.g. calendar event created)
        # 2. It's a system call (user_id contains "system")
        # 3. We are forcing a format (e.g. JSON)
        # 4. It is a system event/role (not a real user message)
        if not system_context and "system" not in user_id and not format and role == "user":
            preset_response = self.check_preset_response(user_message)
            if preset_response:
                # Add to history
                if add_to_history:
                    await self.add_to_history(user_id, "user", user_message)
                    await self.add_to_history(user_id, "assistant", preset_response)
                
                # Detect emotion
                emotion = self.detect_emotion(preset_response)
                
                # Get conversation info
                conv_id = self.active_conversations.get(user_id)
                current_title = None
                if conv_id:
                    conv = conversation_service.get_conversation(user_id, conv_id)
                    if conv:
                        current_title = conv.get("title")
                
                return {
                    "text": preset_response,
                    "emotion": emotion,
                    "conversation_id": conv_id,
                    "conversation_title": current_title
                }
        
        # Add original user message to history
        if add_to_history:
            await self.add_to_history(user_id, role, user_message)
        
        # Get current conversation ID
        conv_id = self.active_conversations.get(user_id)
        current_title = None
        if conv_id:
            conv = conversation_service.get_conversation(user_id, conv_id)
            if conv:
                current_title = conv.get("title")
        
        # Build context from conversation history
        history = self.get_conversation_history(user_id)
        
        # Create prompt with system instructions and history
        # Inject current date/time into system prompt
        from datetime import datetime
        current_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt_with_context = self.system_prompt.replace("{{CURRENT_DATETIME}}", current_dt)
        
        full_prompt = f"{prompt_with_context}\n\n"
        
        # Add recent conversation context (last N messages from config)
        recent_history = history[-(CONTEXT_WINDOW+1):-1] if len(history) > 1 else []
        if recent_history:
            full_prompt += "Recent conversation:\n"
            for msg in recent_history:
                # Map roles to display names
                if msg["role"] == "user":
                    role_name = "User"
                elif msg["role"] == "system":
                    role_name = "System Event"
                else:
                    role_name = "Suzune"
                
                full_prompt += f"{role_name}: {msg['content']}\n"
            full_prompt += "\n"
        
        # Add the current message with appropriate role label
        current_role_name = "User"
        if role == "system":
            current_role_name = "System Event"
            
        full_prompt += f"{current_role_name}: {user_message}\n"
        
        
        if system_context:
            full_prompt += f"\n{system_context}\nJSON Response:"
        else:
            full_prompt += "Suzune:"
        
        # Generate response with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Initialize options dictionary
                options = {}
                if temperature is not None:
                    print(f"🌡️ Setting temperature to: {temperature}")
                    options["temperature"] = temperature
                
                print(f"📤 Sending to Ollama: Format={format}, Options={options}")

                # Call Ollama API with streaming enabled for faster response
                response = await asyncio.to_thread(
                    self.client.generate,
                    model=self.model_name,
                    prompt=full_prompt,
                    format=format,
                    stream=False,  # Keep False for now - streaming needs different handling
                    options=options
                )
                
                ai_text = response['response'].strip()
                
                # Add AI response to history (skip when add_to_history=False, e.g. tool JSON generation)
                if add_to_history:
                    await self.add_to_history(user_id, "assistant", ai_text)
                
                # Detect emotion from the response
                emotion = self.detect_emotion(ai_text)
                
                return {
                    "text": ai_text,
                    "emotion": emotion,
                    "conversation_id": conv_id,
                    "conversation_title": current_title
                }
                
            except Exception as e:
                error_str = str(e)
                print(f"⚠️ Ollama error (attempt {attempt + 1}/{max_retries}): {e}")
                
                # Retry with exponential backoff
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    print(f"⏳ Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Ollama failed after {max_retries} attempts")
                    break
        
        # Fallback response if all retries failed
        return {
            "text": "I apologize, but I'm having trouble processing that right now. Could you try again?",
            "emotion": "neutral",
            "conversation_id": conv_id,
            "conversation_title": current_title
        }

    def detect_emotion(self, text: str) -> str:
        """
        Detect emotion from text using keyword analysis
        
        Returns one of: happy, sad, angry, excited, thoughtful, surprised, neutral
        """
        text_lower = text.lower()
        
        # Count matches for each emotion using config
        emotion_scores = {}
        for emotion, keywords in EMOTION_KEYWORDS.items():
            emotion_scores[emotion] = sum(1 for keyword in keywords if keyword in text_lower)
        
        # Check for exclamation marks (excitement indicator)
        if text.count('!') >= 2:
            emotion_scores['excited'] = emotion_scores.get('excited', 0) + 2
        
        # Check for question marks (thoughtful indicator)
        if text.count('?') >= 2:
            emotion_scores['thoughtful'] = emotion_scores.get('thoughtful', 0) + 1
        
        # Get the emotion with highest score
        if emotion_scores:
            max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            # Return the emotion if score is significant, otherwise neutral
            if max_emotion[1] >= 1:
                return max_emotion[0]
        
        return 'neutral'

    def clear_history(self, user_id: str):
        """Clear conversation history for a user (deprecated - use clear_active_conversation instead)"""
        # This method is deprecated but kept for backward compatibility
        self.clear_active_conversation(user_id)

    async def generate_response_streaming(self, user_message: str, user_id: str, system_context: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate AI response using Ollama with SENTENCE-LEVEL streaming
        Yields each complete sentence as soon as it's generated
        
        Args:
            user_message: The user's input message
            user_id: Unique identifier for the user
            system_context: Optional temporary context to inject
            
        Yields:
            Dictionary with 'sentence', 'is_final', 'full_text', 'emotion' keys
        """
        # Check for preset responses first
        if not system_context and "system" not in user_id:
            preset_response = self.check_preset_response(user_message)
            if preset_response:
                # Add to history
                await self.add_to_history(user_id, "user", user_message)
                await self.add_to_history(user_id, "assistant", preset_response)
                
                # Get conversation info
                conv_id = self.active_conversations.get(user_id)
                current_title = None
                if conv_id:
                    conv = conversation_service.get_conversation(user_id, conv_id)
                    if conv:
                        current_title = conv.get("title")
                
                # Yield as single sentence (NOT final yet - we want sentence processing)
                emotion = self.detect_emotion(preset_response)
                yield {
                    "sentence": preset_response,
                    "is_final": False,
                    "full_text": preset_response,
                    "emotion": emotion,
                    "conversation_id": conv_id,
                    "conversation_title": current_title,
                    "sentence_index": 1
                }
                
                # Then yield final marker
                yield {
                    "sentence": "",
                    "is_final": True,
                    "full_text": preset_response,
                    "emotion": emotion,
                    "conversation_id": conv_id,
                    "conversation_title": current_title,
                    "sentence_index": 1
                }
                return
        
        # Add user message to history
        await self.add_to_history(user_id, "user", user_message)
        
        # Get conversation info
        conv_id = self.active_conversations.get(user_id)
        current_title = None
        if conv_id:
            conv = conversation_service.get_conversation(user_id, conv_id)
            if conv:
                current_title = conv.get("title")
        
        # Build context
        history = self.get_conversation_history(user_id)
        
        from datetime import datetime
        current_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt_with_context = self.system_prompt.replace("{{CURRENT_DATETIME}}", current_dt)
        
        full_prompt = f"{prompt_with_context}\n\n"
        
        # Add recent conversation context
        recent_history = history[-(CONTEXT_WINDOW+1):-1] if len(history) > 1 else []
        if recent_history:
            full_prompt += "Recent conversation:\n"
            for msg in recent_history:
                role_name = "User" if msg["role"] == "user" else "Suzune"
                full_prompt += f"{role_name}: {msg['content']}\n"
            full_prompt += "\n"
        
        full_prompt += f"User: {user_message}\n"
        
        if system_context:
            full_prompt += f"\n{system_context}\n"
            
        full_prompt += "Suzune:"
        
        try:
            # Call Ollama with streaming enabled
            response_stream = await asyncio.to_thread(
                self.client.generate,
                model=self.model_name,
                prompt=full_prompt,
                stream=True,  # Enable streaming!
                options={}
            )
            
            # Buffer for sentence building
            buffer = ""
            full_text = ""
            sentence_count = 0
            
            # Sentence ending patterns
            sentence_enders = re.compile(r'([.!?]+[\s\n]+|[.!?]+$)')
            
            # Process streaming chunks
            for chunk in response_stream:
                chunk_text = chunk.get('response', '')
                buffer += chunk_text
                full_text += chunk_text
                
                # Check if we have complete sentences
                while True:
                    match = sentence_enders.search(buffer)
                    if match:
                        # Extract complete sentence
                        sentence = buffer[:match.end()].strip()
                        buffer = buffer[match.end():]
                        
                        if sentence:
                            sentence_count += 1
                            print(f"📝 Sentence {sentence_count}: {sentence[:50]}...")
                            
                            # Yield the sentence
                            yield {
                                "sentence": sentence,
                                "is_final": False,
                                "full_text": full_text.strip(),
                                "emotion": self.detect_emotion(sentence),
                                "conversation_id": conv_id,
                                "conversation_title": current_title,
                                "sentence_index": sentence_count
                            }
                    else:
                        break
            
            # Handle any remaining text in buffer
            if buffer.strip():
                sentence_count += 1
                print(f"📝 Final fragment {sentence_count}: {buffer[:50]}...")
                yield {
                    "sentence": buffer.strip(),
                    "is_final": False,
                    "full_text": full_text.strip(),
                    "emotion": self.detect_emotion(buffer),
                    "conversation_id": conv_id,
                    "conversation_title": current_title,
                    "sentence_index": sentence_count
                }
            
            # Send final marker
            full_text_clean = full_text.strip()
            emotion = self.detect_emotion(full_text_clean)
            
            # Add complete response to history
            await self.add_to_history(user_id, "assistant", full_text_clean)
            
            yield {
                "sentence": "",
                "is_final": True,
                "full_text": full_text_clean,
                "emotion": emotion,
                "conversation_id": conv_id,
                "conversation_title": current_title,
                "sentence_index": sentence_count
            }
            
            print(f"✅ Streaming complete: {sentence_count} sentences, {len(full_text_clean)} chars")
            
        except Exception as e:
            print(f"❌ Streaming error: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback response
            yield {
                "sentence": "I apologize, but I'm having trouble processing that right now.",
                "is_final": True,
                "full_text": "I apologize, but I'm having trouble processing that right now.",
                "emotion": "neutral",
                "conversation_id": conv_id,
                "conversation_title": current_title,
                "sentence_index": 1
            }

# Create singleton instance
ollama_service = OllamaService()
