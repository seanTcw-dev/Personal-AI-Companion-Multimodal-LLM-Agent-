
import os
import asyncio
import logging
import random
import webbrowser
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from app.services.email_service import email_service
from app.services.news_service import news_service
from app.services.ai_service import ai_service
from app.services.pdf_service import pdf_service
import re

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://example.com") 

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global Variable to store the chat_id
LATEST_CHAT_ID = None

# Sandbox Directory
# Sandbox Directory
# Ensure it is always consistent regardless of where python is run from
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # app/services
BACKEND_DIR = os.path.dirname(os.path.dirname(BASE_DIR)) # backend
SANDBOX_DIR = os.path.join(BACKEND_DIR, "user_files")

if not os.path.exists(SANDBOX_DIR):
    os.makedirs(SANDBOX_DIR)
    logger.info(f"Created sandbox directory at: {SANDBOX_DIR}")
else:
    logger.info(f"Using sandbox directory at: {SANDBOX_DIR}")

# --- Daily Briefing & Email Logic ---

async def send_daily_briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generates and sends a daily briefing using AI."""
    try:
        # 1. Fetch Data
        emails = email_service.get_emails(5)
        news = news_service.get_latest_news(5)
        if update:
            await update.message.reply_text("⏳ Fetching data & drafting content...")

        # 2. Generate Briefing via AI
        # We need a method in ai_service to summarize this data
        briefing_text = await ai_service.generate_briefing_content(emails, news)
        
        # 3. Send
        target_chat_id = update.effective_chat.id if update else LATEST_CHAT_ID
        
        if target_chat_id:
            await context.bot.send_message(
                chat_id=target_chat_id, 
                text=briefing_text, 
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        else:
            logger.warning("No active chat_id for briefing.")

    except Exception as e:
        logger.error(f"Failed to generate briefing: {e}")
        if update:
             await update.message.reply_text("❌ Failed to generate briefing.")

async def manual_briefing_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually triggers the briefing."""
    global LATEST_CHAT_ID
    LATEST_CHAT_ID = update.effective_chat.id
    await send_daily_briefing(context)

async def manual_email_trigger(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manually triggers an email generation (without briefing)."""
    # This command still generates one email for testing purposes
    email = email_service.generate_email()
    await update.message.reply_text(f"📧 Generated new email from: {email['sender_name']}")

# --- Standard Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message with Menu."""
    user = update.effective_user
    global LATEST_CHAT_ID
    LATEST_CHAT_ID = update.effective_chat.id # Store for push notifications
    
    # Web App Button (Opens the Anime Chatbot)
    web_app_button = InlineKeyboardButton(
        text="Open Anime Chatbot 🤖", 
        web_app=WebAppInfo(url=f"{FRONTEND_URL}") 
    )
    
    keyboard = InlineKeyboardMarkup([
        [web_app_button],
        [InlineKeyboardButton("📂 List Files", callback_data="list_files")],
        [InlineKeyboardButton("📰 Daily Briefing", callback_data="get_briefing")]
    ])

    await update.message.reply_text(
        f"Hi {user.first_name}! I am your Anime Chatbot Assistant via Telegram.\n\n"
        "You can control files or open the full 3D interface below.\n"
        "ℹ️ *Note*: I will send you a Daily Briefing every 60s for demo purposes.",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def create_folder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Creates a folder in the sandbox directory."""
    try:
        if not context.args:
            await update.message.reply_text("Usage: /mkdir <foldername>")
            return

        folder_name = context.args[0]
        # Security Check: Prevent path traversal
        if ".." in folder_name or "/" in folder_name or "\\" in folder_name:
            await update.message.reply_text("⚠️ Security Alert: Invalid folder name.")
            return

        target_path = os.path.join(SANDBOX_DIR, folder_name)
        
        if os.path.exists(target_path):
             await update.message.reply_text(f"Folder '{folder_name}' already exists.")
        else:
            os.makedirs(target_path)
            await update.message.reply_text(f"✅ Folder '{folder_name}' created in {SANDBOX_DIR}")

    except Exception as e:
        logger.error(f"Error creating folder: {e}")
        await update.message.reply_text("Failed to create folder.")

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lists files in the sandbox directory."""
    try:
        files = os.listdir(SANDBOX_DIR)
        if not files:
            await update.message.reply_text("📂 The sandbox folder is empty.")
        else:
            file_list = "\n".join([f"- {f}" for f in files])
            await update.message.reply_text(f"📂 Files in Sandbox:\n{file_list}")
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        await update.message.reply_text("Failed to list files.")

import json

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes text messages using the AI Service."""
    if not update.message or not update.message.text:
        return

    user_id = str(update.effective_user.id)
    user_text = update.message.text
    
    # Indicate typing status
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Get AI Response
    response = await ai_service.process_message(user_id, user_text)
    
    # DEBUG: Log the raw response to see what's happening
    logger.info(f"🤖 RAW AI RESPONSE: {response!r}")

    # CHECK FOR TOOL CALL (JSON)
    try:
        # Use regex to find the FIRST valid JSON object in the string
        # This handles cases like: "Sure, here is the tool: { ... }"
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            logger.info(f"🔍 Found potential JSON: {json_str}")
            
            tool_data = json.loads(json_str)
            
            # Verify it's actually a tool call
            if "tool" in tool_data:
                tool_name = tool_data.get("tool")
                params = tool_data.get("parameters", {})
                
                logger.info(f"🛠️ Executing Tool: {tool_name}")
                
                # --- Tool Execution Logic ---
                if tool_name == "create_file":
                    filename = params.get("filename")
                    content = params.get("content")
                    
                    if ".." in filename or "/" in filename or "\\" in filename:
                        await update.message.reply_text("⚠️ AI attempted invalid filename.")
                        return
                    
                    file_path = os.path.join(SANDBOX_DIR, filename)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    await update.message.reply_text(f"✅ AI Created file: `{filename}`")
                    return

                elif tool_name == "read_file":
                    filename = params.get("filename")
                    file_path = os.path.join(SANDBOX_DIR, filename)
                    if os.path.exists(file_path):
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        await update.message.reply_text(f"📄 Content of {filename}:\n```\n{content}\n```", parse_mode='Markdown')
                    else:
                        await update.message.reply_text(f"❌ AI tried to read {filename}, but it does not exist.")
                    return
                
                elif tool_name == "edit_file":
                    filename = params.get("filename")
                    content = params.get("content")
                    file_path = os.path.join(SANDBOX_DIR, filename)
                    if os.path.exists(file_path):
                        with open(file_path, "a", encoding="utf-8") as f:
                            f.write("\n" + content)
                        await update.message.reply_text(f"✅ AI Appended to file: `{filename}`")
                    else:
                        await update.message.reply_text(f"❌ AI tried to edit {filename}, but it does not exist.")
                    return

                elif tool_name == "generate_briefing":
                    await update.message.reply_text("🔄 analyzing data streams... (AI Thinking)")
                    # Execute the actual logic
                    await send_daily_briefing(update, context)
                    return

                elif tool_name == "analyze_pdf":
                    filename = params.get("filename")
                    query = params.get("query")
                    
                    if ".." in filename or "/" in filename or "\\" in filename:
                        await update.message.reply_text("⚠️ AI attempted invalid filename.")
                        return

                    await update.message.reply_text(f"📖 Reading {filename}...")
                    
                    # 1. Extract Text
                    pdf_text = pdf_service.extract_text(filename)
                    
                    if not pdf_text:
                        await update.message.reply_text(f"❌ Failed to read PDF: {filename}. Is it in the folder?")
                        return
                        
                    await update.message.reply_text(f"🧠 Analyzing content ({len(pdf_text)} chars)...")
                    
                    # 2. Ask AI to analyze
                    # We can reuse ai_service.process_message but with context, OR add a specific method.
                    # Let's add a robust method in AIService for this RAG task.
                    analysis = await ai_service.analyze_pdf_content(pdf_text, query)
                    
                    await update.message.reply_text(analysis, parse_mode='Markdown')
                    return

                elif tool_name == "open_url":
                    url_input = params.get("url", "")
                    query = params.get("query", "")
                    
                    # URL mapping for common websites
                    url_shortcuts = {
                        "youtube": "https://www.youtube.com",
                        "google": "https://www.google.com",
                        "gmail": "https://mail.google.com",
                        "github": "https://github.com",
                        "twitter": "https://twitter.com",
                        "facebook": "https://facebook.com",
                        "reddit": "https://reddit.com",
                        "netflix": "https://www.netflix.com",
                        "spotify": "https://open.spotify.com",
                        "amazon": "https://www.amazon.com",
                        "wikipedia": "https://www.wikipedia.org",
                        "instagram": "https://www.instagram.com",
                        "linkedin": "https://www.linkedin.com",
                        "twitch": "https://www.twitch.tv",
                        "discord": "https://discord.com"
                    }
                    
                    # Search URL templates for common sites
                    search_templates = {
                        "youtube": "https://www.youtube.com/results?search_query={}",
                        "google": "https://www.google.com/search?q={}",
                        "github": "https://github.com/search?q={}",
                        "reddit": "https://www.reddit.com/search/?q={}",
                        "amazon": "https://www.amazon.com/s?k={}",
                        "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search={}"
                    }
                    
                    # Determine the final URL
                    url_lower = url_input.lower().strip()
                    
                    if query:
                        # If there's a search query, use search template
                        if url_lower in search_templates:
                            final_url = search_templates[url_lower].format(query.replace(" ", "+"))
                            display_name = url_lower.capitalize()
                        else:
                            # Fallback to Google search
                            final_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                            display_name = "Google"
                    elif url_lower in url_shortcuts:
                        # Use shortcut mapping
                        final_url = url_shortcuts[url_lower]
                        display_name = url_lower.capitalize()
                    elif url_input.startswith("http://") or url_input.startswith("https://"):
                        # Direct URL
                        final_url = url_input
                        display_name = url_input
                    else:
                        # Assume it's a domain name
                        final_url = f"https://{url_input}"
                        display_name = url_input
                    
                    try:
                        # Open the URL in the default browser
                        webbrowser.open(final_url)
                        
                        if query:
                            await update.message.reply_text(f"✅ Opened {display_name} search for: \"{query}\"")
                        else:
                            await update.message.reply_text(f"✅ Opened: {display_name}")
                        
                        logger.info(f"🌐 Opened URL: {final_url}")
                    except Exception as e:
                        logger.error(f"Failed to open URL: {e}")
                        await update.message.reply_text(f"❌ Failed to open URL: {str(e)}")
                    
                    return

        else:
            logger.info("ℹ️ No JSON found in response.")

    except json.JSONDecodeError:
        logger.warning(f"⚠️ Failed to parse JSON from AI response: {response}")
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")

    # If no tool was executed (or if it was just chat), reply with the text
    await update.message.reply_text(response)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sorry, I didn't understand that command.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles file uploads (PDFs) and saves them to sandbox."""
    document = update.message.document
    file_name = document.file_name
    
    # Check extension
    if not file_name.lower().endswith('.pdf'):
        await update.message.reply_text("⚠️ I currently only support .pdf files for analysis.")
        return

    # Security Check
    if ".." in file_name or "/" in file_name or "\\" in file_name:
         await update.message.reply_text("⚠️ Security Alert: Invalid filename.")
         return
         
    # Define PDF Sandbox
    pdf_dir = os.path.join(SANDBOX_DIR, "pdf_uploads")
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    file = await context.bot.get_file(document.file_id)
    target_path = os.path.join(pdf_dir, file_name)
    
    await file.download_to_drive(target_path)
    
    await update.message.reply_text(
        f"✅ Received **{file_name}**.\n"
        f"You can now ask me to analyze it!\n"
        f"Example: 'Analyze {file_name} and tell me the main points.'"
    )

# --- File Operations ---

async def create_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Creates a new file with optional content."""
    try:
        if not context.args:
            await update.message.reply_text("Usage: /create <filename> [content...]")
            return

        filename = context.args[0]
        content = " ".join(context.args[1:]) if len(context.args) > 1 else ""

        # Security Check
        if ".." in filename or "/" in filename or "\\" in filename:
            await update.message.reply_text("⚠️ Security Alert: Invalid filename.")
            return

        file_path = os.path.join(SANDBOX_DIR, filename)
        
        if os.path.exists(file_path):
            await update.message.reply_text(f"⚠️ File '{filename}' already exists. Use /edit to append or /overwrite to replace.")
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            await update.message.reply_text(f"✅ File '{filename}' created.")

    except Exception as e:
        logger.error(f"Error creating file: {e}")
        await update.message.reply_text(f"Failed to create file: {str(e)}")

async def read_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reads the content of a file."""
    try:
        if not context.args:
            await update.message.reply_text("Usage: /read <filename>")
            return

        filename = context.args[0]
        # Security Check
        if ".." in filename or "/" in filename or "\\" in filename:
            await update.message.reply_text("⚠️ Security Alert: Invalid filename.")
            return

        file_path = os.path.join(SANDBOX_DIR, filename)

        if not os.path.exists(file_path):
            await update.message.reply_text(f"❌ File '{filename}' not found.")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        if not content:
            content = "(Empty File)"
            
        await update.message.reply_text(f"📄 **{filename}**:\n```\n{content}\n```", parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error reading file: {e}")
        await update.message.reply_text(f"Failed to read file: {str(e)}")

async def edit_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Appends content to an existing file."""
    try:
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /edit <filename> <content_to_append>")
            return

        filename = context.args[0]
        content = " ".join(context.args[1:])

        # Security Check
        if ".." in filename or "/" in filename or "\\" in filename:
            await update.message.reply_text("⚠️ Security Alert: Invalid filename.")
            return

        file_path = os.path.join(SANDBOX_DIR, filename)

        if not os.path.exists(file_path):
            await update.message.reply_text(f"❌ File '{filename}' does not exist. Use /create first.")
            return

        with open(file_path, "a", encoding="utf-8") as f:
            f.write("\n" + content)
            
        await update.message.reply_text(f"✅ Content appended to '{filename}'.")

    except Exception as e:
        logger.error(f"Error editing file: {e}")
        await update.message.reply_text(f"Failed to edit file: {str(e)}")

# --- Main Run Function ---

def run_telegram_bot():
    """Starts the Telegram Bot."""
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing in .env")
        return

    async def post_init(application):
        commands = [
            BotCommand("start", "Main Menu"),
            BotCommand("briefing", "Get Daily Briefing"),
            BotCommand("create", "Create file"),
            BotCommand("read", "Read file"),
            BotCommand("edit", "Append to file"),
            BotCommand("ls", "List files"),
            BotCommand("mkdir", "Create folder"),
            BotCommand("test_email", "Test Email Gen")
        ]
        await application.bot.set_my_commands(commands)
        logger.info("✅ COMMANDS SET SUFFERFULLY! You should see the menu now.")

    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mkdir", create_folder))
    application.add_handler(CommandHandler("ls", list_files))
    application.add_handler(CommandHandler("create", create_file))
    application.add_handler(CommandHandler("read", read_file))
    application.add_handler(CommandHandler("cat", read_file)) # Alias
    application.add_handler(CommandHandler("edit", edit_file))
    application.add_handler(CommandHandler("briefing", manual_briefing_trigger)) 
    application.add_handler(CommandHandler("test_email", manual_email_trigger))
    
    # Handle Text Messages (AI Chat)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # Handle Document Uploads (PDFs)
    application.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    # Job Queue for Periodic Tasks
    job_queue = application.job_queue
    if job_queue:
        # Scheduled briefing removed in favor of on-demand AI briefing
        logger.info("📅 Job Queue initialized.")
    else:
        logger.warning("⚠️ JobQueue not available. Install 'python-telegram-bot[job-queue]'")

    logger.info("🤖 Telegram Bot is polling...")
    application.run_polling()

if __name__ == '__main__':
    run_telegram_bot()
