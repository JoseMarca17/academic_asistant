import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponses
from pydantic import BaseModel
from assistant.search import query_text
from assistant.brain import get_ai_answer
from assistant.brain import generate_response
from typing import List
from ingest.unified import unify

app = FastAPI(title="Academic Assistant API")

BASE_WEB_DIR = os.path.dirname(os.path.abspath(__file__))

class Message(BaseModel):
    role: str 
    content: str

class ChatRequest(BaseModel):
    question: str
    history: List[Message]

@app.get("/")
def home():
    return FileResponses(os.path.join(BASE_WEB_DIR, "templates", "index.html"))

@app.post("/ask")
async def ask(request: ChatRequest):
    try:
        results = query_text(request.question)
        
        historial_data = [m.model_dump() for m in request.history]
        answer = get_ai_answer(request.question, results, [m.dict() for m in request.history])
        
        return{
            "answer": answer,
            "sources": list(set([r['ruta'] for r in results]))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/unify")
async def run_unify():
    try:
        unify()
        return {
            "status": "success",
            "message": "Apuntes unificados exitosamente"
        }
    except Exception as e:
        raise HTTPException(status_code=500, details=str(e))

if __name__ == "__main__":
    uvicorn.run("app", host="127.0.0.1", port=8000)