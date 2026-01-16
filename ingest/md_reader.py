import os
import yaml
import json
from datetime import date, datetime
from config import VAULT_PATH, EXCLUDED_FOLDERS

OUTPUT_PATH = 'data/processed/notas.json' 

def read_md_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            metadata_raw = parts[1]
            body = parts[2].strip()
            try:
                metadata = yaml.safe_load(metadata_raw)
            except yaml.YAMLError:
                metadata = {}
        else:
            metadata = {}
            body = content
    else:
        metadata = {}
        body =  content
    
    return metadata, body

def make_json_safe(obj):
    if isinstance(obj, dict):
        return {k:make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(i) for i in obj]
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    else:
        return obj
    

def walk_vault(vault_path):
    notes = []
    
    for root, dirs, files in os.walk(vault_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                metadata, body = read_md_file(full_path)
                note = {
                    "ruta": os.path.relpath(full_path, vault_path),
                    "metadata": make_json_safe(metadata),
                    "contenido": body 
                }
                notes.append(note)
    
    return notes

def save_json(data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok = True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"[+] Guardadas {len(data)} notas en {output_path}")

if __name__ == "__main__":
    notes = walk_vault(VAULT_PATH)
    save_json(notes, OUTPUT_PATH)
