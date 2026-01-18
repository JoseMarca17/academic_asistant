import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.Client()
collection = client.get_or_create_collection("academic_knowledge")
model = SentenceTransformer("all-MiniLM-L6-v2")

def query_text(text, top_k=3):
    
    total_docs = len(collection.get()['ids'])
    if total_docs == 0:
        return [{
            "texto": "No hay documentos indexados aun",
            "ruta": "",
            "tipo": ""
        }]
    emb = model.encode(text).tolist()
    
    results = collection.query(
        query_embeddings=[emb],
        n_results=top_k
    )
    
    docs = []
    documentos = results['documents'][0]
    metadatos = results['metadata'][0]
    
    for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
        docs.append({
            "texto":doc,
            "ruta": metadata["ruta"],
            "tipo": metadata["tipo"]
        })
    
    return docs

if __name__ == "__main__":
    pregunta = input("Que quieres buscar? ")
    resultados = query_text(pregunta)
    for r in resultados:
        print(f"-> [{r['tipo']}] {r['ruta']}: {r['texto'][:200]}...")