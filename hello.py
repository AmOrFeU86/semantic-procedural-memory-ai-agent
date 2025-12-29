import requests
import os
import json

# Coloca tu API key aquí o mejor como variable de entorno
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or "TU_API_KEY_AQUI"

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    # Opcionales pero recomendados por OpenRouter
    "HTTP-Referer": "http://localhost",
    "X-Title": "hello-example"
}

# Archivo de memoria persistente
MEMORY_FILE = "long_term_memory.json"
MAX_MEMORY_FACTS = 30  # Límite de hechos importantes
EXTRACTION_INTERVAL = 5  # Extraer hechos cada N pares de mensajes (user+assistant)

# Memoria de sesión: historial de mensajes
conversation_history = []
message_count = 0  # Contador de pares de mensajes
last_extraction_index = 0  # Índice del último mensaje procesado

def load_memory():
    """
    Carga la memoria de largo plazo desde el archivo JSON.
    """
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando memoria: {e}")
            return []
    return []

def save_memory(memory):
    """
    Guarda la memoria de largo plazo en el archivo JSON.
    """
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error guardando memoria: {e}")

# Cargar memoria al inicio
long_term_memory = load_memory()

def get_memory_context():
    """
    Genera un texto con los hechos importantes de la memoria de largo plazo.
    """
    if not long_term_memory:
        return ""

    facts_text = "\n".join([f"- {fact}" for fact in long_term_memory])
    return f"\n\n### Hechos importantes que recuerdas:\n{facts_text}\n"

def send_message(user_message):
    """
    Envía un mensaje al modelo y mantiene el historial de conversación.
    """
    # Agregar el mensaje del usuario al historial
    conversation_history.append({"role": "user", "content": user_message})

    # Preparar mensajes con contexto de memoria de largo plazo
    messages = []

    # Si hay memoria de largo plazo, añadir como contexto del sistema
    if long_term_memory:
        memory_context = get_memory_context()
        messages.append({
            "role": "system",
            "content": f"Eres un asistente útil. Tienes acceso a información importante de conversaciones anteriores:{memory_context}"
        })

    # Añadir el historial de la conversación actual
    messages.extend(conversation_history)

    data = {
        "model": "x-ai/grok-4.1-fast",
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    # Obtener la respuesta del asistente
    assistant_message = result["choices"][0]["message"]["content"]

    # Agregar la respuesta del asistente al historial
    conversation_history.append({"role": "assistant", "content": assistant_message})

    return assistant_message

def is_duplicate_fact(new_fact, existing_facts):
    """
    Verifica si un hecho ya existe en la memoria (con cierta tolerancia).
    """
    new_fact_lower = new_fact.lower().strip()

    for existing_fact in existing_facts:
        existing_fact_lower = existing_fact.lower().strip()

        # Verificación exacta
        if new_fact_lower == existing_fact_lower:
            return True

        # Verificación de similitud alta (uno contiene al otro con >80% de longitud)
        if new_fact_lower in existing_fact_lower or existing_fact_lower in new_fact_lower:
            shorter = min(len(new_fact_lower), len(existing_fact_lower))
            longer = max(len(new_fact_lower), len(existing_fact_lower))
            if shorter / longer > 0.8:
                return True

    return False

def find_similar_fact(new_fact, existing_facts, threshold=0.6):
    """
    Busca un hecho similar en la memoria existente basado en palabras clave comunes.
    Retorna el índice del hecho similar o None.
    """
    new_words = set(new_fact.lower().split())

    for idx, existing_fact in enumerate(existing_facts):
        existing_words = set(existing_fact.lower().split())

        # Calcular similitud basada en palabras comunes
        if len(new_words) > 0 and len(existing_words) > 0:
            common_words = new_words.intersection(existing_words)
            similarity = len(common_words) / max(len(new_words), len(existing_words))

            if similarity > threshold:
                return idx

    return None

def extract_important_facts(force=False):
    """
    Usa el LLM para extraer hechos importantes de la conversación reciente.

    Args:
        force: Si es True, extrae aunque no haya llegado al intervalo.
               Útil al terminar la conversación.
    """
    global long_term_memory, last_extraction_index

    # Solo extraer si hay suficiente conversación
    if len(conversation_history) < 2:
        return

    # Determinar qué mensajes analizar
    if force or last_extraction_index == 0:
        # Al forzar o en la primera extracción, analizar desde la última extracción
        messages_to_analyze = conversation_history[last_extraction_index:]
    else:
        # En modo periódico, analizar los nuevos mensajes
        messages_to_analyze = conversation_history[last_extraction_index:]

    # Si no hay mensajes nuevos, no hacer nada
    if not messages_to_analyze:
        return

    # Limitar a los últimos 10 mensajes para no saturar el contexto
    if len(messages_to_analyze) > 10:
        messages_to_analyze = messages_to_analyze[-10:]

    # Preparar contexto de memoria actual para el LLM
    memory_context = ""
    if long_term_memory:
        memory_list = "\n".join([f"{i+1}. {fact}" for i, fact in enumerate(long_term_memory)])
        memory_context = f"\n\nMEMORIA ACTUAL:\n{memory_list}\n"

    # Crear un prompt para que el LLM extraiga hechos importantes
    extraction_prompt = {
        "role": "user",
        "content": f"""Analiza esta conversación y extrae hechos importantes.{memory_context}
IMPORTANTE: Si la conversación contiene información que ACTUALIZA o CONTRADICE algo de la memoria actual, debes indicarlo.

Responde en formato JSON con esta estructura:
{{
  "new_facts": ["hecho nuevo 1", "hecho nuevo 2"],
  "updates": [
    {{"old": "texto del hecho a reemplazar (debe coincidir con la memoria)", "new": "nuevo hecho actualizado"}}
  ]
}}

Incluye en new_facts:
- Información personal del usuario (nombre, preferencias, contexto, profesión, intereses)
- Decisiones o conclusiones importantes
- Procedimientos o métodos aprendidos
- Objetivos o metas mencionadas

Incluye en updates:
- Cambios de preferencias (ej: antes le gustaba X, ahora prefiere Y)
- Correcciones de información
- Actualizaciones de estado o situación

NO incluyas:
- Saludos o despedidas
- Conversación trivial
- Información temporal o irrelevante
- Hechos obvios o demasiado generales

Si no hay hechos nuevos ni actualizaciones, responde: {{"new_facts": [], "updates": []}}

Sé muy selectivo."""
    }

    extraction_messages = messages_to_analyze + [extraction_prompt]

    data = {
        "model": "x-ai/grok-4.1-fast",
        "messages": extraction_messages
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()

        # Obtener la respuesta
        facts_text = result["choices"][0]["message"]["content"]

        # Intentar parsear como JSON
        try:
            # Limpiar la respuesta si tiene formato de código
            if "```json" in facts_text:
                facts_text = facts_text.split("```json")[1].split("```")[0].strip()
            elif "```" in facts_text:
                facts_text = facts_text.split("```")[1].split("```")[0].strip()

            extraction_result = json.loads(facts_text)

            # Verificar que tenga el formato correcto
            if not isinstance(extraction_result, dict):
                extraction_result = {"new_facts": [], "updates": []}

            new_facts = extraction_result.get("new_facts", [])
            updates = extraction_result.get("updates", [])

            changes_made = False

            # Procesar actualizaciones primero
            if updates and isinstance(updates, list):
                for update in updates:
                    if isinstance(update, dict) and "old" in update and "new" in update:
                        old_text = update["old"]
                        new_text = update["new"]

                        # Buscar el hecho a actualizar (búsqueda exacta o similar)
                        updated = False
                        for idx, fact in enumerate(long_term_memory):
                            if fact.lower().strip() == old_text.lower().strip():
                                # Reemplazo exacto
                                long_term_memory[idx] = new_text
                                print(f"[Actualizado: '{old_text}' → '{new_text}']")
                                updated = True
                                changes_made = True
                                break

                        # Si no se encontró exacto, buscar similar
                        if not updated:
                            similar_idx = find_similar_fact(old_text, long_term_memory)
                            if similar_idx is not None:
                                old_fact = long_term_memory[similar_idx]
                                long_term_memory[similar_idx] = new_text
                                print(f"[Actualizado: '{old_fact}' → '{new_text}']")
                                changes_made = True

            # Procesar nuevos hechos
            if new_facts and isinstance(new_facts, list):
                # Filtrar hechos duplicados
                unique_facts = []
                for fact in new_facts:
                    if not is_duplicate_fact(fact, long_term_memory):
                        unique_facts.append(fact)

                if unique_facts:
                    # Añadir nuevos hechos únicos a la memoria
                    long_term_memory.extend(unique_facts)
                    changes_made = True

                    print(f"[Memoria: {len(unique_facts)} nuevo(s) hecho(s) añadido(s)]")
                elif len(new_facts) > 0:
                    # Todos eran duplicados
                    print(f"[{len(new_facts)} hecho(s) duplicado(s) ignorado(s)]")

            # Limitar el número de hechos (FIFO)
            if len(long_term_memory) > MAX_MEMORY_FACTS:
                removed = len(long_term_memory) - MAX_MEMORY_FACTS
                long_term_memory = long_term_memory[-MAX_MEMORY_FACTS:]
                print(f"[{removed} hecho(s) antiguo(s) eliminado(s) por límite]")
                changes_made = True

            # Guardar en disco si hubo cambios
            if changes_made:
                save_memory(long_term_memory)

            # Actualizar el índice de última extracción
            last_extraction_index = len(conversation_history)

        except json.JSONDecodeError as e:
            print(f"[Error parseando JSON de extracción: {e}]")

    except Exception as e:
        print(f"[Error extrayendo hechos: {e}]")

# Bucle principal de conversación
print("=" * 60)
print("Agente de IA con memoria semántica-procedural de largo plazo")
print("=" * 60)
print(f"Hechos almacenados en memoria: {len(long_term_memory)}")
print(f"Extracción de memoria cada {EXTRACTION_INTERVAL} mensajes")
print("Escribe 'salir' o 'exit' para terminar.")
print("Escribe 'memoria' para ver los hechos guardados.")
print("Escribe 'guardar' para forzar guardado de memoria.\n")

while True:
    user_input = input("Tú: ")

    if user_input.lower() in ["salir", "exit", "quit"]:
        # Extraer hechos antes de salir si hay mensajes sin procesar
        if len(conversation_history) > last_extraction_index:
            print("\n[Procesando memoria antes de salir...]")
            extract_important_facts(force=True)
        print("¡Hasta luego!")
        break

    if user_input.lower() == "memoria":
        if long_term_memory:
            print("\n=== Memoria de Largo Plazo ===")
            for i, fact in enumerate(long_term_memory, 1):
                print(f"{i}. {fact}")
            print(f"\nTotal: {len(long_term_memory)}/{MAX_MEMORY_FACTS} hechos\n")
        else:
            print("\nLa memoria está vacía.\n")
        continue

    if user_input.lower() == "guardar":
        print("\n[Forzando extracción de memoria...]")
        extract_important_facts(force=True)
        continue

    if not user_input.strip():
        continue

    try:
        response = send_message(user_input)
        print(f"Asistente: {response}\n")

        # Incrementar contador de mensajes (cada par user+assistant)
        message_count += 1

        # Extraer hechos importantes periódicamente
        if message_count % EXTRACTION_INTERVAL == 0:
            print(f"[Actualizando memoria... ({message_count} mensajes)]")
            extract_important_facts()

    except Exception as e:
        print(f"Error: {e}\n")
