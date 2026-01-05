"""Configuración del agente de IA con memoria de largo plazo."""
import os

# API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or "TU_API_KEY_AQUI"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "x-ai/grok-4.1-fast"

# Headers para la API
API_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost",
    "X-Title": "semantic-memory-agent"
}

# Memoria
MEMORY_FILE = "long_term_memory.json"
MAX_FACTS = 30
EXTRACTION_INTERVAL = 3  # cada N mensajes
