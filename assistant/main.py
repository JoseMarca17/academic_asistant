from fastapi import FastAPI
from pydantic import BaseModel
from assistant.search import query_text
from assistant.brain import generate_response

app = FastAPI(title="Academic Assistant API")

class QueryRequest(BaseModel):
    prompt: str

@app.post("/ask")
async def ask_assistant(request: QueryRequest):
    relevant_chunks = query_text(request.prompt, top_k=4)
    
    ai_answer = generate_response(request.prompt, relevant_chunks)
    
    return {
        "answer": ai_answer,
        "sources": [c['ruta'] for c in relevant_chunks]
    }