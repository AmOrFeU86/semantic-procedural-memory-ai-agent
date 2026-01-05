"""Extracción de hechos importantes de conversaciones."""
import json
import requests
from config import API_URL, MODEL, API_HEADERS
from memory import is_duplicate, apply_limit, save_memory


def create_prompt(memory):
    """Crea el prompt de extracción con el contexto de memoria actual."""
    memory_context = ""
    if memory:
        memory_list = "\n".join([f"{i+1}. {fact}" for i, fact in enumerate(memory)])
        memory_context = f"\n\nMEMORIA ACTUAL:\n{memory_list}\n"

    return f"""Analiza esta conversación y extrae hechos importantes.{memory_context}

Responde en formato JSON:
{{
  "new_facts": ["hecho nuevo 1", "hecho nuevo 2"]
}}

Incluye en new_facts:
- Información personal del usuario (nombre, preferencias, profesión, intereses)
- Decisiones o conclusiones importantes
- Procedimientos aprendidos
- Objetivos mencionados

NO incluyas: saludos, conversación trivial, información temporal irrelevante.

Si no hay hechos nuevos: {{"new_facts": []}}

Sé selectivo."""


def call_api(messages):
    """Llama a la API para extraer hechos."""
    response = requests.post(API_URL, headers=API_HEADERS, json={
        "model": MODEL,
        "messages": messages
    })
    return response.json()


def parse_response(facts_text):
    """Parsea la respuesta JSON del LLM."""
    # Limpiar markdown si existe
    if "```json" in facts_text:
        facts_text = facts_text.split("```json")[1].split("```")[0].strip()
    elif "```" in facts_text:
        facts_text = facts_text.split("```")[1].split("```")[0].strip()

    data = json.loads(facts_text)
    if not isinstance(data, dict):
        return []

    return data.get("new_facts", [])


def process_new_facts(new_facts, memory):
    """Procesa y añade nuevos hechos a la memoria."""
    added = 0
    duplicates = 0

    for fact in new_facts:
        if not is_duplicate(fact, memory):
            memory.append(fact)
            added += 1
        else:
            duplicates += 1

    if added > 0:
        print(f"[Memoria: {added} nuevo(s) hecho(s) añadido(s)]")
    if duplicates > 0:
        print(f"[{duplicates} hecho(s) duplicado(s) ignorado(s)]")

    return added > 0


def extract_facts(conversation_history, memory, last_extraction_index):
    """
    Extrae hechos importantes de la conversación.

    Returns:
        Nuevo índice de última extracción
    """
    # Validar que hay suficiente conversación
    if len(conversation_history) < 2:
        return last_extraction_index

    # Obtener mensajes desde la última extracción
    messages = conversation_history[last_extraction_index:]
    if not messages:
        return last_extraction_index

    # Crear prompt de extracción
    prompt = create_prompt(memory)
    messages.append({"role": "user", "content": prompt})

    # Llamar a la API y procesar
    try:
        result = call_api(messages)
        facts_text = result["choices"][0]["message"]["content"]

        # Parsear respuesta
        new_facts = parse_response(facts_text)

        # Procesar cambios
        changes = False

        if new_facts:
            if process_new_facts(new_facts, memory):
                changes = True

        # Aplicar límite
        memory[:], removed = apply_limit(memory)
        if removed > 0:
            print(f"[{removed} hecho(s) antiguo(s) eliminado(s) por límite]")
            changes = True

        # Guardar si hubo cambios
        if changes:
            save_memory(memory)

        return len(conversation_history)

    except Exception as e:
        print(f"[Error extrayendo hechos: {e}]")
        return last_extraction_index
