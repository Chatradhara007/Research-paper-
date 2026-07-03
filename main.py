import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

load_dotenv(override=True)

# Import core modules
from core.loader import save_uploaded_file, parse_document
from core.processor import generate_summary_and_flowchart
from core.vector_db import build_index
from core.chat import chat_with_memory, set_new_document_context


app = FastAPI(title="AI Research Paper Assistant")

# Serve the static frontend
os.makedirs("static", exist_ok=True)
os.makedirs("uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return f.read()

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_path = await save_uploaded_file(file, "uploads")
        chunks = parse_document(file_path)
        build_index(chunks)
        set_new_document_context(file.filename)
        summary_data = generate_summary_and_flowchart(chunks)
        return JSONResponse(content={"status": "success", "summary": summary_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        reply = chat_with_memory(request.message)
        return JSONResponse(content={"reply": reply})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
