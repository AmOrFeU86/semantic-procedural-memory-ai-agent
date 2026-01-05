"""Funciones para gestionar la memoria de largo plazo."""
import json
import os
from config import MEMORY_FILE, MAX_FACTS


def load_memory():
    """Carga la memoria desde el archivo JSON."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando memoria: {e}")
    return []


def save_memory(memory):
    """Guarda la memoria en el archivo JSON."""
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error guardando memoria: {e}")


def is_duplicate(new_fact, memory):
    """Verifica si un hecho ya existe en la memoria."""
    new_lower = new_fact.lower().strip()

    for fact in memory:
        fact_lower = fact.lower().strip()

        # Coincidencia exacta
        if new_lower == fact_lower:
            return True

        # Similitud alta (uno contiene al otro y >80% similar)
        if new_lower in fact_lower or fact_lower in new_lower:
            shorter = min(len(new_lower), len(fact_lower))
            longer = max(len(new_lower), len(fact_lower))
            if shorter / longer > 0.8:
                return True

    return False


def find_similar(text, memory, threshold=0.6):
    """Busca un hecho similar basado en palabras comunes."""
    text_words = set(text.lower().split())

    for idx, fact in enumerate(memory):
        fact_words = set(fact.lower().split())

        if len(text_words) > 0 and len(fact_words) > 0:
            common = text_words.intersection(fact_words)
            similarity = len(common) / max(len(text_words), len(fact_words))

            if similarity > threshold:
                return idx

    return None


def apply_limit(memory):
    """Aplica el límite de hechos (FIFO)."""
    if len(memory) > MAX_FACTS:
        removed = len(memory) - MAX_FACTS
        return memory[-MAX_FACTS:], removed
    return memory, 0


def get_memory_context(memory):
    """Retorna el contexto de memoria formateado para el LLM."""
    if not memory:
        return ""
    facts = "\n".join([f"- {fact}" for fact in memory])
    return f"\n\n### Hechos importantes que recuerdas:\n{facts}\n"


def show_memory(memory):
    """Muestra la memoria guardada."""
    if memory:
        print("\n=== Memoria de Largo Plazo ===")
        for i, fact in enumerate(memory, 1):
            print(f"{i}. {fact}")
        print(f"\nTotal: {len(memory)}/{MAX_FACTS} hechos\n")
    else:
        print("\nLa memoria está vacía.\n")
