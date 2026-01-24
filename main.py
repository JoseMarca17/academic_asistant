import os
import json
import uvicorn
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

from assistant.search import query_text
from assistant.brain import get_ai_answer
from ingest.unified import unify

app = FastAPI(title="Academic Assistant")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "web", "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "web", "templates")
CHATS_DIR = os.path.join(BASE_DIR, "data", "chats")

if not os.path.exists(CHATS_DIR):
    os.makedirs(CHATS_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: List[Message]

@app.get("/")
async def home():
    return FileResponse(os.path.join(TEMPLATE_DIR, "index.html"))

@app.post("/ask")
async def ask(request: ChatRequest):
    try:
        results = query_text(request.question)
        historial_dict = [m.model_dump() for m in request.history]
        answer = get_ai_answer(request.question, results, historial_dict)
        return {
            "answer": answer,
            "sources": list(set([r['ruta'] for r in results]))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/admin/unify")
async def run_unify():
    try:
        unify()
        return {"message": "Notas unificadas y base de datos actualizada."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chats")
async def list_chats():
    chats = []
    for filename in os.listdir(CHATS_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(CHATS_DIR, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                chats.append({"id": data["id"], "title": data["title"]})
    return chats

@app.get("/api/chats/{chat_id}")
async def get_chat(chat_id: str):
    path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.post("/api/chats")
async def create_chat():
    chat_id = str(uuid.uuid4())
    new_chat = {"id": chat_id, "title": "Nueva Conversación", "messages": []}
    path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(new_chat, f, indent=4, ensure_ascii=False)
    return new_chat

@app.post("/api/chats/{chat_id}/message")
async def save_message(chat_id: str, message: Message):
    path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Archivo de chat no encontrado")
    
    with open(path, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["messages"].append(message.model_dump())
        if len(data["messages"]) == 1:
            data["title"] = message.content[:30] + ("..." if len(message.content) > 30 else "")
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.truncate()
    return {"status": "ok"}

@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    path = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Chat no encontrado")
    os.remove(path)
    return {"status": "deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)