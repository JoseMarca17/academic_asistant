import json
import chromadb
from sentence_transformers import SentenceTransformer
from config import Config

def split_text(text, chunk_size, overlap):
    chunks = []
    start = 0 
    
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            last_break =  text.rfind(".", start, end)
            if last_break == -1:
                last_break = text.rfind("\n", start, end)
            if last_break != -1 and last_break > start + (chunk_size // 2):
                end = last_break + 1 
        chunks.append(text[start:end].strip())
        start =  end -  overlap
    return chunks

def build_index():
    if not Config.UNIFIED_JSON.exists():
        print(f"[!] No se encontró {Config.UNIFIED_JSON}")
        return

    with open(Config.UNIFIED_JSON, "r", encoding="utf-8") as f:
        notas = json.load(f)

    client = chromadb.PersistentClient(path=Config.CHROMA_PATH)
    collection = client.get_or_create_collection("academic_knowledge")
    model = SentenceTransformer(Config.MODEL_NAME)

    ids, embeddings, documents, metadatas = [], [], [], []

    for nota in notas:
        texto = nota.get("contenido", "")
        if len(texto) < 10: continue

        chunks = split_text(texto, Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{nota['id']}_ch_{i}"
            
            ids.append(chunk_id)
            documents.append(chunk)
            embeddings.append(model.encode(chunk).tolist())
            metadatas.append({
                "ruta": nota["ruta"],
                "tipo": nota["tipo"]
            })

    collection.add(
        ids=ids, 
        documents=documents, 
        metadatas=metadatas, 
        embeddings=embeddings
    )
    print(f"[+] Éxito: {len(documents)} fragmentos indexados en ChromaDB.")

if __name__ == "__main__":
    build_index()