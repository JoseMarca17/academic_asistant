import json
import os
from sentence_transformers import SentenceTransformer
import chromadb


DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/processed/unified.json")
DATA_PATH = os.path.normpath(DATA_PATH)


CHUNK_SIZE = 500  
CHUNK_OVERLAP = 50  

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    i = 0
    while i < len(words):
        chunk = words[i:i+size]
        yield " ".join(chunk)
        i += size - overlap

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    print("[*] Cargando datos...")
    if not os.path.exists(DATA_PATH):
        print(f"[!] No se encontró {DATA_PATH}. Ejecutá primero unify_data.py")
        return

    docs = load_json(DATA_PATH)
    print(f"[+] {len(docs)} documentos cargados")

    print("[*] Inicializando modelo de embeddings...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("[+] Modelo cargado")

    print("[*] Conectando con ChromaDB...")
    client = chromadb.Client()
    collection = client.get_or_create_collection(name="academic_knowledge")
    print("[+] Conexión lista")

    total_chunks = 0
    for doc_id, doc in enumerate(docs):
        for i, chunk in enumerate(chunk_text(doc["contenido"])):
            total_chunks += 1
            embedding = model.encode(chunk).tolist()
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{
                    "ruta": doc["ruta"],
                    "tipo": doc["tipo"]
                }],
                ids=[f"{doc_id}_{i}"]
            )
            if i % 5 == 0:
                print(f"[>] Procesando doc {doc_id}, chunk {i}")

    print(f"[+] Proceso finalizado. Total de chunks indexados: {total_chunks}")

if __name__ == "__main__":
    main()
