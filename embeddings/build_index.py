import os
import json
import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "academic_knowledge"
VAULT_PATH = "data/processed/unified.json"  
MODEL_NAME = "all-MiniLM-L6-v2"

client = chromadb.Client()
collection = client.get_or_create_collection(COLLECTION_NAME)
model = SentenceTransformer(MODEL_NAME)

def build_index():
    if not os.path.exists(VAULT_PATH):
        print(f"[!] No se encontró {VAULT_PATH}")
        return

    with open(VAULT_PATH, "r", encoding="utf-8") as f:
        notas = json.load(f)

    if not notas:
        print("[!] No hay notas para indexar")
        return

    ids = []
    embeddings = []
    metadatas = []
    documents = []

    for i, nota in enumerate(notas):
        texto = nota.get("texto", "")
        if not texto.strip():
            continue

        emb = model.encode(texto).tolist()
        embeddings.append(emb)
        documents.append(texto)
        metadatas.append({
            "ruta": nota.get("ruta", "Desconocida"),
            "tipo": nota.get("tipo", "Desconocido")
        })
        ids.append(f"doc_{i}")

    if not documents:
        print("[!] No se generaron documentos válidos para indexar")
        return

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(f"[+] Se indexaron {len(documents)} documentos exitosamente.")

if __name__ == "__main__":
    build_index()
