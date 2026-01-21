from assistant.search import query_text
from assistant.brain import get_ai_answer

pregunta = "como se imprime en python"

print("🔍 Buscando en tus apuntes...")
resultados = query_text(pregunta)

print("🧠 Generando respuesta inteligente...\n")
respuesta_final = get_ai_answer(pregunta, resultados)

print("================ ASISTENTE ACADÉMICO ================")
print(respuesta_final)
print("=====================================================")