"""Agente de IA con memoria semántica-procedural de largo plazo."""
import requests
from config import API_URL, MODEL, EXTRACTION_INTERVAL, MAX_FACTS, API_HEADERS
from memory import load_memory, get_memory_context
from extraction import extract_facts


# Estado global
long_term_memory = load_memory()
conversation_history = []
message_count = 0
last_extraction_index = 0


def send_message(user_message):
    """Envía un mensaje al LLM con contexto de memoria."""
    conversation_history.append({"role": "user", "content": user_message})

    # Preparar mensajes con memoria
    messages = []
    if long_term_memory:
        messages.append({
            "role": "system",
            "content": f"Eres un asistente útil. Tienes acceso a información importante de conversaciones anteriores:{get_memory_context(long_term_memory)}"
        })
    messages.extend(conversation_history)

    # Llamar a la API
    response = requests.post(API_URL, headers=API_HEADERS, json={
        "model": MODEL,
        "messages": messages
    })
    result = response.json()
    assistant_message = result["choices"][0]["message"]["content"]

    conversation_history.append({"role": "assistant", "content": assistant_message})
    return assistant_message


def main():
    """Bucle principal."""
    global message_count, last_extraction_index

    print("=" * 60)
    print("Agente de IA con memoria semántica-procedural de largo plazo")
    print("=" * 60)
    print(f"Hechos almacenados: {len(long_term_memory)}")
    print(f"Extracción automática cada {EXTRACTION_INTERVAL} mensajes")
    print("Escribe 'salir' para terminar\n")

    while True:
        user_input = input("Tú: ")

        # Comando salir
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("¡Hasta luego!")
            break

        if not user_input.strip():
            continue

        # Mensaje normal
        try:
            response = send_message(user_input)
            print(f"Asistente: {response}\n")

            message_count += 1

            # Extraer periódicamente
            if message_count % EXTRACTION_INTERVAL == 0:
                print(f"[Actualizando memoria... ({message_count} mensajes)]")
                last_extraction_index = extract_facts(
                    conversation_history, long_term_memory, last_extraction_index
                )

        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
