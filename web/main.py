from fastapi import FastAPI
from pydantic import BaseModel
from assistant import search
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

app = FastAPI()
templates = Jinja2Templates(directory="web/templates")

class Pregunta(BaseModel):
    texto: str

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request":request})

@app.post("/query")
def query(p: Pregunta):
    resultados = search.query_text(p.texto, top_k=3)
    if not resultados:
        return {
            "resultados": [], 
            "mensaje": "No se encontro nada relevante"
        }
    return {"resultados": resultados}

