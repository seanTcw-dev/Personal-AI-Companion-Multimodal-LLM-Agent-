from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
from typing import List

router = APIRouter()

# Define Sandbox Directory (Same as TelegramBot/PDFService)
# Define Sandbox Directory (Same as TelegramBot/PDFService)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # app/api -> app/
BACKEND_DIR = os.path.dirname(BASE_DIR) # app/ -> backend/
SANDBOX_DIR = os.path.join(BACKEND_DIR, "user_files", "pdf_uploads")

if not os.path.exists(SANDBOX_DIR):
    os.makedirs(SANDBOX_DIR)

@router.post("/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the sandbox directory.
    """
    try:
        # Security check for filename
        if ".." in file.filename or "/" in file.filename or "\\" in file.filename:
             raise HTTPException(status_code=400, detail="Invalid filename")
             
        file_path = os.path.join(SANDBOX_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {
            "filename": file.filename,
            "status": "success", 
            "message": f"File '{file.filename}' uploaded successfully."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def list_files():
    """List files in the sandbox."""
    files = os.listdir(SANDBOX_DIR)
    return {"files": files}
