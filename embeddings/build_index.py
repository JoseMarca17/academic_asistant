import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "academic_knowledge"
TOP_K = 3
PREVIEW_LENGTH = 200  

client = chromadb.Client()
collection = client.get_or_create_collection(COLLECTION_NAME)
model = SentenceTransformer("all-MiniLM-L6-v2")

def query_text(text, top_k=TOP_K):
    
    if collection.count() == 0:
        print("[!] La colección está vacía. Ejecuta build_index.py primero.")
        return []

    emb = model.encode(text).tolist()

    results = collection.query(
        query_embeddings=[emb],
        n_results=top_k
    )

    docs = []
    documents = results.get('documents', [[]])[0]
    metadatas = results.get('metadatas', [[]])[0]

    if not documents:
        print("[!] No se encontraron resultados para tu búsqueda.")
        return []

    for doc, metadata in zip(documents, metadatas):
        docs.append({
            "texto": doc,
            "ruta": metadata.get("ruta", "Desconocida"),
            "tipo": metadata.get("tipo", "Desconocido")
        })

    print(f"[+] Se encontraron {len(docs)} resultados.")
    return docs

if __name__ == "__main__":
    while True:
        try:
            pregunta = input("🔹 Qué quieres buscar? (escribe 'salir' para terminar) ")
            if pregunta.lower() in {"salir", "exit"}:
                break

            resultados = query_text(pregunta)

            for i, r in enumerate(resultados, 1):
                preview = r['texto'][:PREVIEW_LENGTH].replace("\n", " ")
                print(f"{i}. [{r['tipo']}] {r['ruta']}: {preview}...")

        except KeyboardInterrupt:
            print("\n[!] Interrupción manual. Saliendo...")
            break
        except Exception as e:
            print(f"[!] Error inesperado: {e}")
