import chromadb
from sentence_transformers import SentenceTransformer
from config import Config

client = chromadb.PersistentClient(path=Config.CHROMA_PATH)
collection = client.get_or_create_collection("academic_knowledge")
model = SentenceTransformer(Config.MODEL_NAME)

def query_text(text, top_k=None):
    if top_k is None:
        top_k = Config.TOP_K_RESULTS

    if collection.count() == 0:
        return []

    query_emb = model.encode(text).tolist()

    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k
    )

    formatted_results = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        formatted_results.append({
            "texto": doc,
            "ruta": meta['ruta'],
            "tipo": meta['tipo']
        })
    
    return formatted_results

if __name__ == "__main__":
    pregunta = input("Pregunta a tus apuntes: ")
    res = query_text(pregunta)
    for r in res:
        print(f"\n[{r['tipo']}] -> {r['ruta']}\n{r['texto'][:300]}...\n{'-'*50}")