from google import genai
from config import Config

# Inicializamos el cliente
client = genai.Client(api_key=Config.GEMINI_API_KEY)

def get_ai_answer(question, search_results):
    # Consolidamos el contexto (esto ya lo tenías bien)
    contextText = ""
    for r in search_results:
        contextText += f"\n--- FUENTE: {r['ruta']} ({r['tipo']}) ---\n{r['texto']}\n"

    prompt = f"""
    Actúa como un tutor académico experto y un poco sarcástico. 
    Responde usando este contexto de mis apuntes:
    
    {contextText}
    
    Pregunta: {question}
    
    Reglas: Si no está en las notas, dímelo con un comentario ácido pero ayúdame igual. 
    Usa Markdown para el código.
    """

    # CAMBIO AQUÍ: Probemos quitando el prefijo 'models/' si es que lo tenías, 
    # o simplemente asegurando el nombre directo.
    response = client.models.generate_content(
        model=Config.GEMINI_MODEL, 
        contents=prompt
    )
    
    return response.text