from google import genai
from config import Config

client = genai.Client(api_key=Config.GEMINI_API_KEY)

def get_ai_answer(question, search_results, history =[]):
    contextText = ""
    for r in search_results:
        contextText += f"\n--- FUENTE: {r['ruta']} ({r['tipo']}) ---\n{r['texto']}\n"

    contents = [
        {
            "role": "user", 
            "parts": [{"text": f"Contexto de mis apuntes:\n{contextText}"}]
        },
        {
            "role": "model", 
            "parts": [{"text": "Entendido. Responderé basado en tus notas con un toque sarcástico."}]
        }
    ]
    
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    contents.append({
        "role": "user",
        "parts": [{"text": question}]
    })

    try:
        response = client.models.generate_content(
            model=Config.GEMINI_MODEL,
            contents=contents
        )
        
        return response.text
    except Exception as e:
        print(f"Error en Gemini API: {e}")
        return "Hubo un error al consultar a mi cerebro digital. Inténtalo de nuevo."