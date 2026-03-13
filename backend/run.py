import uvicorn
import subprocess
import sys
import os
import signal
import atexit

telegram_process = None

def start_telegram_bot():
    """Spawn a separate process to run the Telegram bot"""
    global telegram_process
    
    # Get the current Python executable (respects conda/venv)
    python_exe = sys.executable
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("🤖 Starting Telegram Bot in a separate process...")
    
    # Launch telegram bot as a subprocess with CREATE_NEW_CONSOLE on Windows
    # This opens a new CMD window so you can see Telegram bot logs separately
    creation_flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    
    telegram_process = subprocess.Popen(
        [python_exe, "-m", "app.services.telegram_bot"],
        cwd=backend_dir,
        creationflags=creation_flags,
    )
    
    print(f"✅ Telegram Bot started (PID: {telegram_process.pid})")

def cleanup():
    """Terminate Telegram bot process on exit"""
    global telegram_process
    if telegram_process and telegram_process.poll() is None:
        print("🛑 Shutting down Telegram Bot...")
        telegram_process.terminate()
        try:
            telegram_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            telegram_process.kill()
        print("✅ Telegram Bot stopped.")

if __name__ == "__main__":
    # Register cleanup to stop Telegram bot when FastAPI exits
    atexit.register(cleanup)
    
    # Start Telegram bot in a new console window
    start_telegram_bot()
    
    # Start FastAPI server (main process)
    print("🚀 Starting FastAPI server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)