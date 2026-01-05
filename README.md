# Agente de IA con Memoria Semántica-Procedural de Largo Plazo

Un chatbot inteligente que utiliza **memoria de largo plazo persistente** para recordar información importante entre sesiones. El agente aprende automáticamente sobre ti, tus preferencias, y puede actualizar su conocimiento cuando la información cambia.

## 🌟 Características Principales

### 💾 Memoria Persistente
- **Almacenamiento en disco**: Los hechos importantes se guardan en formato JSON
- **Persistencia entre sesiones**: La memoria se mantiene aunque cierres y vuelvas a abrir el programa
- **Límite configurable**: Mantiene hasta 30 hechos importantes (configurable)

### 🧠 Extracción Inteligente de Hechos
- **Detección automática**: El LLM decide qué información es importante guardar
- **Extracción periódica**: Analiza la conversación cada 5 mensajes (configurable)
- **Evita duplicados**: Sistema de deduplicación automática basado en similitud

### ⚡ Eficiencia
- **Extracción periódica**: Solo actualiza memoria cada N mensajes, no en cada interacción
- **Guardado al salir**: Procesa mensajes pendientes antes de cerrar
- **Control manual**: Comando para forzar guardado cuando lo necesites

## 📋 Requisitos

- Python 3.7+
- Biblioteca `requests`
- API Key de OpenRouter (para acceder a modelos LLM)

## 🚀 Instalación

1. **Clona el repositorio o descarga el archivo**:
```bash
git clone <repository-url>
cd semantic-procedural-memory-ai-agent
```

2. **Instala las dependencias**:
```bash
pip install requests
```

3. **Configura tu API Key**:

Opción A - Variable de entorno (recomendado):
```bash
export OPENROUTER_API_KEY="tu-api-key-aqui"
```

Opción B - Editar el archivo:
```python
# En hello.py, línea 6
OPENROUTER_API_KEY = "tu-api-key-aqui"
```

## 💻 Uso

### Iniciar el programa

```bash
python main.py
```

### Comandos disponibles

- **Conversar normalmente**: Simplemente escribe tus mensajes
- **`salir` / `exit` / `quit`**: Termina el programa

**Nota**: La memoria se actualiza automáticamente cada 5 mensajes en segundo plano. No necesitas hacer nada más que conversar.

### Ejemplo de sesión

```
============================================================
Agente de IA con memoria semántica-procedural de largo plazo
============================================================
Hechos almacenados en memoria: 0
Extracción de memoria cada 5 mensajes
Escribe 'salir' o 'exit' para terminar.
Escribe 'memoria' para ver los hechos guardados.
Escribe 'guardar' para forzar guardado de memoria.

Tú: Hola, me llamo Juan y soy desarrollador de Python
Asistente: ¡Hola Juan! Encantado de conocerte. Es genial que seas desarrollador de Python...

Tú: Me encantan las películas de ciencia ficción
Asistente: ¡Excelente! La ciencia ficción es un género fascinante...

[Después de 5 mensajes...]
[Actualizando memoria... (5 mensajes)]
[Memoria: 2 nuevo(s) hecho(s) añadido(s)]

Tú: memoria

=== Memoria de Largo Plazo ===
1. El usuario se llama Juan
2. Es desarrollador de Python
3. Le encantan las películas de ciencia ficción

Total: 3/30 hechos
```

## 🔧 Configuración

Puedes personalizar el comportamiento editando las constantes en `config.py`:

```python
# Configuración de Memoria
MEMORY_FILE = "long_term_memory.json"
MAX_MEMORY_FACTS = 30  # Cambia a 50 si quieres más capacidad
EXTRACTION_INTERVAL = 5  # Cambia a 3 para actualizar más seguido, 10 para menos

# Umbrales de Similitud
DUPLICATE_THRESHOLD = 0.8  # Para deduplicación (0.0 - 1.0)
SIMILARITY_THRESHOLD = 0.6  # Para búsqueda de similitud (0.0 - 1.0)

# Configuración del LLM
MODEL_NAME = "x-ai/grok-4.1-fast"  # Cambia aquí el modelo
MAX_MESSAGES_TO_ANALYZE = 10  # Máximo de mensajes a analizar por extracción
```

## 🧪 Cómo Funciona

### 1. Memoria de Sesión vs Largo Plazo

**Memoria de Sesión** (`conversation_history`):
- Almacena toda la conversación actual
- Se borra al cerrar el programa
- Permite al LLM entender el contexto inmediato

**Memoria de Largo Plazo** (`long_term_memory`):
- Almacena solo hechos importantes
- Persiste en disco (`long_term_memory.json`)
- Se carga automáticamente al iniciar

### 2. Proceso de Extracción

```
Conversación (5 mensajes) → LLM Analiza → Extrae hechos importantes
                                        ↓
                            Verifica duplicados
                                        ↓
                            Añade a memoria
                                        ↓
                              Guarda en disco (JSON)
```

### 3. Deduplicación

Tres niveles de verificación:
- **Exacta**: Compara textos idénticos (ignorando mayúsculas)
- **Similitud alta**: Detecta hechos con >80% de contenido común
- **Similitud temática**: Encuentra hechos sobre el mismo tema (>60% palabras comunes)

## 📁 Estructura de Archivos

```
semantic-procedural-memory-ai-agent/
│
├── main.py                     # Programa principal (81 líneas)
├── extraction.py               # Extracción de hechos (128 líneas)
├── memory.py                   # Funciones de memoria (89 líneas)
├── config.py                   # Configuración (20 líneas)
├── long_term_memory.json       # Memoria persistente (se crea automáticamente)
└── README.md                   # Este archivo
```

**Total: 318 líneas** - Código simple y mantenible ✅

### Descripción de Módulos

**main.py** - Bucle principal (súper simple)
- `send_message()` - Envía mensajes al LLM con contexto de memoria
- `main()` - Bucle de interacción y comandos

**extraction.py** - Extracción de hechos (dividido en funciones)
- `create_prompt()` - Crea el prompt de extracción
- `call_api()` - Llama a la API del LLM
- `parse_response()` - Parsea la respuesta JSON
- `process_new_facts()` - Procesa y añade nuevos hechos
- `extract_facts()` - Función principal (orquesta todo)

**memory.py** - Gestión de memoria
- `load_memory()` / `save_memory()` - Persistencia en JSON
- `get_memory_context()` - Formatea memoria para el LLM
- `show_memory()` - Muestra la memoria guardada
- `is_duplicate()` - Detecta hechos duplicados
- `apply_limit()` - Aplica límite FIFO

**config.py** - Configuración
- Constantes de API (URL, modelo, headers)
- Configuración de memoria (límites, intervalos)

## 🎯 Casos de Uso

### Asistente Personal
Recuerda tus preferencias, objetivos, y contexto personal para conversaciones más naturales.

### Tutor de Aprendizaje
Mantiene registro de lo que has aprendido, tus dificultades, y tu progreso.

### Organizador de Proyectos
Recuerda decisiones importantes, arquitectura elegida, y contexto del proyecto.

### Compañero de Brainstorming
Mantiene ideas importantes, conclusiones, y evolución de conceptos.

## 🔍 Tipos de Información que Guarda

El LLM está configurado para extraer:

✅ **Información personal**: Nombre, profesión, intereses, contexto
✅ **Preferencias**: Gustos, aversiones, estilos preferidos
✅ **Decisiones importantes**: Elecciones tomadas, conclusiones alcanzadas
✅ **Procedimientos aprendidos**: Métodos, técnicas, workflows
✅ **Objetivos**: Metas mencionadas, planes futuros
✅ **Relaciones**: Conexiones entre conceptos e ideas

❌ **NO guarda**: Saludos, conversación trivial, información temporal irrelevante

## ⚙️ Personalización del Modelo

Por defecto usa `x-ai/grok-4.1-fast`. Para cambiar el modelo, edita `config.py`:

```python
# En config.py
MODEL_NAME = "x-ai/grok-4.1-fast"  # Cambia aquí
```

Modelos recomendados para OpenRouter:
- `x-ai/grok-4.1-fast` - Rápido y eficiente
- `anthropic/claude-3.5-sonnet` - Muy preciso
- `openai/gpt-4` - Excelente comprensión
- `google/gemini-pro` - Buena relación calidad-precio

## 🐛 Solución de Problemas

### La memoria no se guarda
- Verifica que tengas permisos de escritura en el directorio
- Revisa que no haya errores en la consola
- Usa el comando `guardar` para forzar el guardado

### Se guardan hechos duplicados
- El sistema ya tiene deduplicación, pero puedes ajustar el threshold en `config.py`:
```python
DUPLICATE_THRESHOLD = 0.9  # Cambia de 0.8 a 0.9 para ser más estricto
```

### La memoria crece demasiado rápido
- Ajusta estos valores en `config.py`:
```python
EXTRACTION_INTERVAL = 10  # Aumentar para extraer menos frecuentemente
MAX_MEMORY_FACTS = 20  # Reducir para mantener menos hechos
```

## 📊 Formato del archivo JSON

El archivo `long_term_memory.json` tiene este formato:

```json
[
  "El usuario se llama Juan",
  "Es desarrollador de Python con 5 años de experiencia",
  "Prefiere programación funcional sobre orientada a objetos",
  "Le encantan las películas de ciencia ficción",
  "Está aprendiendo Rust"
]
```

Puedes editarlo manualmente si lo necesitas, pero asegúrate de mantener el formato de array JSON válido.

## 🤝 Contribuciones

Este es un proyecto educativo. Siéntete libre de:
- Hacer fork del repositorio
- Experimentar con diferentes prompts
- Añadir nuevas funcionalidades
- Probar diferentes modelos LLM

## 📝 Licencia

Este proyecto es de código abierto y está disponible para uso educativo y personal.

## 🙏 Créditos

- Utiliza la API de [OpenRouter](https://openrouter.ai/) para acceso a modelos LLM
- Modelo por defecto: Grok 4.1 Fast de xAI
