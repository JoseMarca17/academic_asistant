import os 
import json
from PyPDF2 import PdfReader
from config import VAULT_PATH, EXCLUDED_FOLDERS

OUTPUT_PATH = "data/processed/pdfs.json"

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        print(f"[!] Error al leer {pdf_path}: {e}")
        return ""

def walk_vault_for_pdfs(vaul_path):
    pdfs = []
    
    for root, dirs, files in os.walk(vaul_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_FOLDERS]
        
        for file in files:
            if file.lower().endswith(".pdf"):
                full_path = os.path.join(root, file)
                text = extract_text_from_pdf(full_path)
                
                if text:
                    pdfs.append({
                        "ruta": os.path.relpath(full_path, vaul_path),
                        "contenido": text
                    })
    
    return pdfs

def save_json(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=True)
    print(f"[+] Guardados {len(data)} PDFs en {output_path}")

if __name__ == "__main__":
    pdfs = walk_vault_for_pdfs(VAULT_PATH)
    save_json(pdfs, OUTPUT_PATH)