import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    VAULT_PATH = Path(r"G:\My Drive\ObsidianVault")
    EXCLUDED_FOLDERS = {"Templates", ".obsidian", ".trash"}

    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    PROCESSED_DIR = DATA_DIR / "processed"
    
    UNIFIED_JSON = PROCESSED_DIR / "unified.json"
    CHROMA_PATH = str(DATA_DIR / "chroma")  
    
    MODEL_NAME = "all-MiniLM-L6-v2"
    GEMINI_MODEL = "gemini-3-flash-preview"
    
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 150 
    TOP_K_RESULTS = 4