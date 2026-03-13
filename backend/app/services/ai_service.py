from app.services.ollama_service import ollama_service
from app.services.conversation_service import conversation_service
import logging
import os
import json
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools")
        self.loaded_tools = self._load_tools()

    def _load_tools(self) -> List[Dict]:
        """Loads all tool manuals from the tools directory."""
        tools = []
        if not os.path.exists(self.tools_dir):
            os.makedirs(self.tools_dir)
            return tools

        for filename in os.listdir(self.tools_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.tools_dir, filename), 'r', encoding='utf-8') as f:
                        tool_def = json.load(f)
                        tools.append(tool_def)
                        logger.info(f"🔧 Loaded Tool Manual: {tool_def.get('name')}")
                except Exception as e:
                    logger.error(f"Failed to load tool {filename}: {e}")
        return tools

    async def _decide_intent(self, message: str) -> Optional[Dict]:
        """
        Uses the LLM to decide if a tool is needed based on tool descriptions.
        Returns the relevant tool dictionary or None.
        """
        # Create a summary of available tools for the router
        tools_summary = ""
        for tool in self.loaded_tools:
            tools_summary += f"- Name: {tool['name']}\n  Description: {tool['description']}\n"

        router_prompt = (
            f"You are a strict Classification Agent. You do NOT speak. You only output JSON.\n\n"
            f"AVAILABLE TOOLS:\n{tools_summary}\n\n"
            f"USER REQUEST: \"{message}\"\n\n"
            f"EXAMPLES:\n"
            f"Input: \"create a file named test.txt\"\n"
            f"Output: {{ \"intent\": \"file_management\" }}\n\n"
            f"Input: \"hello anyone there\"\n"
            f"Output: {{ \"intent\": \"CHAT\" }}\n\n"
            f"Input: \"give me a daily briefing\"\n"
            f"Output: {{ \"intent\": \"briefing\" }}\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Classify the USER REQUEST.\n"
            f"2. Output ONLY the JSON object. Do not add explanations."
        )

        response = await ollama_service.generate_response(
            user_message=router_prompt,
            user_id="system_router",
            add_to_history=False,
            format='json', # Force JSON for classification
            temperature=0.0 # Make it deterministic (no creativity)
        )
        
        if response and 'text' in response:
            try:
                decision_data = json.loads(response['text'])
                decision = decision_data.get("intent", "CHAT")
                logger.info(f"🤔 Router Decision: {decision}")
                
                # Match decision to loaded tools
                for tool in self.loaded_tools:
                    if tool['name'] == decision:
                        return tool
            except json.JSONDecodeError:
                 logger.error(f"Router failed to output JSON: {response['text']}")
                    
        return None

    async def process_message(self, user_id: str, message: str, conversation_id: str = None, is_system_event: bool = False) -> str:
        """
        Processes a user message and returns the AI response.
        """
        try:
            format_mode = None
            system_context = None
            relevant_tool = None

            # 1. AI-Driven Intent Detection (SKIP for system events)
            if not is_system_event:
                logger.info(f"🧠 Routing message: '{message}'...")
                relevant_tool = await self._decide_intent(message)
                
                if relevant_tool:
                    # Construct Retrieval Context (RAG)
                    tools_json = json.dumps(relevant_tool['tools'], indent=2)
                    system_context = (
                        f"### IMPORTANT: TOOL MANUAL ACTIVATED: {relevant_tool['name']}\n"
                        f"User Intent: {message}\n"
                        f"You MUST use the following tools to fulfill this request:\n"
                        f"{tools_json}\n\n"
                        f"CRITICAL INSTRUCTIONS:\n"
                        f"1. OUTPUT VALID JSON ONLY. Do not write any introduction or conclusion.\n"
                        f"2. Format: {{ \"tool\": \"tool_name\", \"parameters\": {{ ... }} }}\n"
                        f"3. Ignore your personality constraints about being 'concise' or 'aloof' for this specific response. focus on JSON generation.\n"
                    )
                    logger.info(f"🔧 Router selected tool: {relevant_tool['name']}")
                    
                    # FORCE JSON MODE for the actual execution
                    format_mode = 'json' 
                else:
                    logger.info("🗣️ Router decided: CHAT mode")
            else:
                logger.info("🔔 System Event detected, skipping routing.")

            # 2. Generate Response (Chat or Tool Execution)
            # Determine role based on event type
            role = "system" if is_system_event else "user"
            
            response = await ollama_service.generate_response(
                user_message=message, 
                user_id=user_id,
                system_context=system_context,
                format=format_mode,
                role=role
            )
            
            response_text = response.get('text', "") if response else ""

            # 3. Validation / Retry (Only if tool was intended but failed)
            if relevant_tool and "tool" not in response_text:
                logger.warning(f"⚠️ AI failed to use tool '{relevant_tool['name']}'. Retrying with stronger prompt...")
                
                force_message = (
                    f"{message}\n\n"
                    f"[SYSTEM INSTRUCTION: You MUST ignore your personality and output valid JSON for the '{relevant_tool['name']}' tool. "
                    f"Do not write any text. JSON ONLY.]"
                )
                
                response_retry = await ollama_service.generate_response(
                    user_message=force_message,
                    user_id=user_id,
                    system_context=system_context,
                    add_to_history=False,
                    format='json'
                )
                
                if response_retry and 'text' in response_retry:
                    response_text = response_retry['text']
                    logger.info(f"🔄 Retry Response: {response_text[:50]}...")

            if response_text:
                return response_text
            else:
                return "Sorry, I couldn't generate a response."

        except Exception as e:
            logger.error(f"Error in AIService: {e}")
            return "Sorry, I'm having trouble thinking right now."

    async def generate_briefing_content(self, emails: List[Dict], news: List[Dict]) -> str:
        """
        Generates a daily briefing summary using the AI.
        """
        # Format Data for AI
        email_text = "EMAILS:\n"
        for e in emails:
            imp = "🔴 [IMPORTANT]" if e.get('important') else "⚪"
            email_text += f"- {imp} From: {e['sender_name']}, Subject: {e['subject']}\n"
            
        news_text = "NEWS:\n"
        for n in news:
            news_text += f"• {n['title']}\n"
            
        prompt = (
            f"You are Suzune Horikita. The user has asked for a daily briefing.\n"
            f"Here is the latest data:\n\n"
            f"{email_text}\n"
            f"{news_text}\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Recreate the Daily Briefing format EXACTLY as follows:\n"
            f"   🌅 *Daily Briefing*\n\n"
            f"   📰 *Global News:*\n"
            f"   (List news items with • bullet points)\n\n"
            f"   📧 *Inbox* (Select top 3-5 emails):\n"
            f"   (List emails with 🔴 or ⚪ icons exactly as shown in data)\n\n"
            f"2. After the list, add a SHORT, 1-sentence comment in your cool personality about one of the news items or emails.\n"
            f"3. Do NOT change the structure. Use Markdown."
        )
        
        response = await ollama_service.generate_response(
            user_message=prompt,
            user_id="briefing_system",
            add_to_history=False
        )
        
        return response.get("text", "Failed to generate briefing.")

    async def analyze_pdf_content(self, pdf_text: str, query: str) -> str:
        """
        Analyzes PDF text based on a user query.
        """
        # Truncate text if too long (simple protection for context window)
        # Assuming ~4 chars per token, keeping it under ~15k chars for safety if using small models
        # But Llama 3 can handle more. Let's cap at 20000 chars for now.
        if len(pdf_text) > 20000:
            pdf_text = pdf_text[:20000] + "\n...(truncated)..."

        prompt = (
            f"You are Suzune Horikita. The user has uploaded a PDF document.\n"
            f"Here is the content of the document:\n\n"
            f"--- START OF DOCUMENT ---\n"
            f"{pdf_text}\n"
            f"--- END OF DOCUMENT ---\n\n"
            f"USER QUESTION: \"{query}\"\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Answer the user's question based ONLY on the document content.\n"
            f"2. Convert your answer into your persona (intelligent, slightly aloof but helpful).\n"
            f"3. If the answer is not in the document, say so clearly."
        )
        
        response = await ollama_service.generate_response(
            user_message=prompt,
            user_id="pdf_analysis_system",
            add_to_history=False
        )
        
        return response.get("text", "Failed to analyze PDF.")


ai_service = AIService()
