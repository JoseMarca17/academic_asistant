import os 
import json

NOTES_PATH = "data/processed/notas.json"
PDFS_PATH = "data/processed/pdfs.json"
OUTPUT_PATH = "data/processed/unified.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def unify():
    unified = []
    
    notes = load_json(NOTES_PATH)
    pdfs = load_json(PDFS_PATH)
    
    for note in notes:
        unified.append({
            "tipo": "md",
            "ruta": note["ruta"],
            "metadata": note.get("metadata", {}),
            "contenido": note["contenido"]
        })
    
    for pdf in pdfs:
        unified.append({
            "tipo": "pdf",
            "ruta": pdf["ruta"],
            "metadata": {},
            "contenido": pdf["contenido"]
        })
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(unified, f, indent=4, ensure_ascii=True)
    
    print(f"[+] Dataset unificado: {len(unified)} documentos")

if __name__ == "__main__":
    unify()