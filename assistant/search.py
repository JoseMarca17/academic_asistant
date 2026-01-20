import chromadb
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "academic_knowledge"
CHROMA_PATH = "data/chroma"
MODEL_NAME = "all-MiniLM-L6-v2"

client = chromadb.Client(
    settings=chromadb.Settings(
        persist_directory=CHROMA_PATH
    )
)

collection = client.get_or_create_collection(COLLECTION_NAME)
model = SentenceTransformer(MODEL_NAME)


def query_text(text, top_k=3):

    total_docs = collection.count()
    if total_docs == 0:
        return [{
            "texto": "No hay documentos indexados aún.",
            "ruta": "",
            "tipo": ""
        }]

    emb = model.encode(text).tolist()

    results = collection.query(
        query_embeddings=[emb],
        n_results=top_k
    )

    docs = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return [{
            "texto": "No se encontró nada relevante para tu consulta.",
            "ruta": "",
            "tipo": ""
        }]

    for doc, metadata in zip(documents, metadatas):
        docs.append({
            "texto": doc,
            "ruta": metadata.get("ruta", ""),
            "tipo": metadata.get("tipo", "")
        })

    return docs


if __name__ == "__main__":
    pregunta = input("¿Qué quieres buscar? ")
    resultados = query_text(pregunta)

    for r in resultados:
        print(f"-> [{r['tipo']}] {r['ruta']}: {r['texto'][:200]}...")
