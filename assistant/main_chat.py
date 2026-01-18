import json
from assistant import search
from transformers import pipeline

TOP_K_RESULTS = 3
PREVIEW_LENGTH = 200
HISTORICO_FILE = "assistant/history.json"  

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

try:
    with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
        historial = json.load(f)
except FileNotFoundError:
    historial = []

def mostrar_resultados(resultados):
    if not resultados:
        print("[!] No hay resultados para mostrar.\n")
        return
    
    for i, r in enumerate(resultados, 1):
        preview = r['texto'][:PREVIEW_LENGTH].replace("\n", " ")
        print(f"{i}. [{r['tipo']}] {r['ruta']}: {preview}...")

def generar_resumen(resultados):
    if not resultados:
        return ""
    
    textos = " ".join([r['texto'] for r in resultados])
    try:
        resumen = summarizer(textos, max_length=150, min_length=60, do_sample=False)
        return resumen[0]['summary_text']
    except Exception as e:
        print(f"[!] Error generando resumen: {e}")
        return ""

def guardar_historial(pregunta, resultados):
    historial.append({
        "pregunta": pregunta,
        "resultados": resultados
    })
    with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4, ensure_ascii=False)

def main():
    print("=== Asistente académico ===")
    print("Escribe 'salir' para terminar\n")

    while True:
        try:
            pregunta = input("Tu pregunta: ").strip()
            if pregunta.lower() in {"salir", "exit"}:
                print("[*] Cerrando asistente...")
                break

            resultados = search.query_text(pregunta, TOP_K_RESULTS)
            mostrar_resultados(resultados)

            resumen = generar_resumen(resultados)
            if resumen:
                print(f"\nResumen de resultados:\n{resumen}\n")

            guardar_historial(pregunta, resultados)

        except KeyboardInterrupt:
            print("\n[!] Interrupción manual. Saliendo...")
            break
        except Exception as e:
            print(f"[!] Error inesperado: {e}")

if __name__ == "__main__":
    main()
