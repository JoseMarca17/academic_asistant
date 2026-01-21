import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles 
from pydantic import BaseModel
from assistant.search import query_text
from assistant.brain import get_ai_answer

app = FastAPI(title="Academic Assistant Pro")

BASE_WEB_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_WEB_DIR, "templates")
STATIC_DIR = os.path.join(BASE_WEB_DIR, "static")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def home():
    html_path = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"error": f"No se encontró el archivo en {html_path}. Verifica que esté dentro de web/templates/"}

@app.post("/ask")
def ask(request: QuestionRequest):
    try:
        results = query_text(request.question)
        if not results:
            return {"answer": "No encontré nada en tus notas. ¿Seguro que estás estudiando?", "sources": []}
        
        answer = get_ai_answer(request.question, results)
        return {
            "answer": answer,
            "sources": list(set([r['ruta'] for r in results])) 
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))