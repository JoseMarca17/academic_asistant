import os
import json
from config import Config

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def clean_text(text):
    return " ".join(text.split())

def unify():
    unified = []
    notes = load_json(Config.PROCESSED_DIR / "notas.json")
    pdfs = load_json(Config.PROCESSED_DIR / "pdfs.json")
    
    for idx, note in enumerate(notes + pdfs):
        tipo = "md" if "metadata" in note else "pdf"
        unified.append({
            "id": f"doc_{idx}",
            "tipo": tipo,
            "ruta": str(note["ruta"]),
            "contenido": clean_text(note["contenido"]),
            "metadata": note.get("metadata", {})
        })
    
    os.makedirs(Config.PROCESSED_DIR, exist_ok=True)
    with open(Config.UNIFIED_JSON, "w", encoding="utf-8") as f:
        json.dump(unified, f, indent=4, ensure_ascii=False)
    
    print(f"[+] Dataset unificado: {len(unified)} documentos en {Config.UNIFIED_JSON}")

if __name__ == "__main__":
    unify()