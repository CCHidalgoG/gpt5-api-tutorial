# OpenAI GPT-5 API Guide & Interactive Playground

Guía práctica y completa para experimentar con las nuevas características de la API del modelo **GPT-5** de OpenAI en Python. El repositorio está estructurado con código modular en `src/`, un Jupyter Notebook interactivo en `notebooks/` y configuración lista para su ejecución.

---

## Estructura del Proyecto

```text
OpenAI GPT-5 API/
├── .env                         # Clave de API de OpenAI (no subir a git)
├── .gitignore                   # Exclusiones de Git
├── requirements.txt             # Dependencias del proyecto
├── README.md                    # Esta documentación
├── src/                         # Módulos Python por característica
│   ├── 01_reasoning_effort.py   # Control de esfuerzo de razonamiento y tokens
│   ├── 02_verbosity.py          # Control de longitud y detalle de respuesta
│   ├── 03_cot_handoff.py        # Multi-turno con traspaso de Chain-of-Thought
│   ├── 04_freeform_input.py     # Entrada libre (SQL/código) en herramientas custom
│   ├── 05_constraining_outputs.py # Salidas restringidas por gramáticas CFG (Lark)
│   ├── 06_allowed_tools.py      # Subconjuntos de herramientas permitidas
│   └── 07_preambles.py          # Explicaciones previas al invocar herramientas
└── notebooks/                   # Jupyter Notebook interactivo
    └── gpt_5_api_tutorial.ipynb # Tutorial interactivo paso a paso
```

---

## Requisitos Previos e Instalación

### 1. Requisitos
- **Python**: 3.10 o superior.
- **OpenAI Python SDK**: versión `openai>=1.60.0`.
- Una clave de API de OpenAI con acceso al modelo `gpt-5`.

### 2. Configuración del Entorno Virtual e Instalación

```bash
# Crear entorno virtual (si no cuentas con uno)
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Variables de Entorno (`.env`)

Copia o configura tu archivo `.env` en la raíz del proyecto:

```bash
OPENAI_API_KEY="sk-proj-..."
```

---

## Nuevas Características de la API de GPT-5

### 1. Nivel de Razonamiento (`Reasoning Effort`)
El parámetro `reasoning={"effort": "..."}` permite balancear precisión, latencia y coste token por token:
- **`minimal`**: Respuesta directa sin asignación de tokens internos de razonamiento. Ideal para tareas rápidas y código simple.
- **`low` / `medium` / `high`**: Despliega cadenas internas de razonamiento profundo para problemas complejos o deducciones matemáticas/lógicas.

```python
resp = client.responses.create(
    model="gpt-5",
    input="¿Quién es el creador de Python?",
    reasoning={"effort": "minimal"},
)
print(resp.output_text)
print(f"Reasoning tokens: {resp.usage.output_tokens_details.reasoning_tokens}")
```

Ejecutar demo:
```bash
python src/01_reasoning_effort.py
```

---

### 2. Control de Verbosidad (`Verbosity`)
Permite definir el nivel de extensión y profundidad de la salida sin necesidad de alterar el prompt del sistema:
- **`low`**: Respuestas breves y directas al grano.
- **`medium`**: Balance entre contexto y concisión.
- **`high`**: Respuestas completas, pedagógicas, con explicaciones paso a paso o comentarios de código.

```python
resp = client.responses.create(
    model="gpt-5",
    input="¿Quién es Guido van Rossum?",
    reasoning={"effort": "minimal"},
    text={"verbosity": "low"},
)
```

Ejecutar demo:
```bash
python src/02_verbosity.py
```

---

### 3. Multi-Turno con Traspaso de Cadena de Pensamiento (`CoT Handoff`)
En la **Responses API**, el parámetro `previous_response_id` permite heredar la memoria interna y la cadena de razonamiento (Chain-of-Thought) de turnos previos. Esto evita que el modelo vuelva a razonar desde cero y ahorra latencia.

```python
first = client.responses.create(
    model="gpt-5",
    input="¿Quién es el padre de Python?",
    reasoning={"effort": "minimal"},
    text={"verbosity": "low"},
)

followup = client.responses.create(
    model="gpt-5",
    previous_response_id=first.id,
    input="Escribe un blog sobre su legado.",
    reasoning={"effort": "medium"},
    text={"verbosity": "high"},
)
```

Ejecutar demo:
```bash
python src/03_cot_handoff.py
```

---

### 4. Entrada Libre en Herramientas (`Freeform Input`)
A diferencia de las APIs tradicionales que exigen esquemas JSON rígidos, las herramientas personalizadas (`type: "custom"`) de GPT-5 pueden recibir **texto plano directo**, como sentencias SQL o código Python, a través del atributo `input`.

```python
tools = [{
    "type": "custom",
    "name": "sql_query_runner",
    "description": "Runs raw SQL queries on the database.",
}]

resp = client.responses.create(model="gpt-5", tools=tools, input=messages)
```

Ejecutar demo:
```bash
python src/04_freeform_input.py
```

---

### 5. Salidas Restringidas por Gramática Libre de Contexto (CFG / Lark)
Para flujos críticos donde las llamadas no pueden fallar en sintaxis, GPT-5 permite adjuntar una gramática en formato **Lark**. El modelo garantiza matemáticamente que el texto generado cumpla dicha gramática.

```python
tools = [{
    "type": "custom",
    "name": "sql_query_runner",
    "format": {
        "type": "grammar",
        "syntax": "lark",
        "definition": lark_grammar,
    },
}]
```

Ejecutar demo:
```bash
python src/05_constraining_outputs.py
```

---

### 6. Subconjuntos de Herramientas Permitidas (`Allowed Tools`)
Permite enviar una lista completa de $N$ herramientas al contexto (para optimizar la caché de prompts), pero restringir al modelo a utilizar únicamente un subconjunto $M < N$ en un turno determinado (`mode: "auto"` o `mode: "required"`).

```python
resp = client.responses.create(
    model="gpt-5",
    input="What's the weather in Oslo?",
    tools=tools,
    tool_choice={
        "type": "allowed_tools",
        "mode": "required",
        "tools": [{"type": "function", "name": "get_weather"}],
    },
)
```

Ejecutar demo:
```bash
python src/06_allowed_tools.py
```

---

### 7. Preámbulos en Ejecución de Herramientas (`Preambles`)
Permite que el modelo proporcione una explicación concisa y legible antes de realizar la invocación de una herramienta, mejorando notablemente la transparencia en flujos agentiles.

```python
msgs = [
    {
        "role": "system",
        "content": "Before you call a tool, explain why you are calling it in ONE short sentence prefixed with 'Preamble:'."
    },
    {"role": "user", "content": "What's the weather in Oslo?"}
]
```

Ejecutar demo:
```bash
python src/07_preambles.py
```

---

### 8. Optimización de Prompts (`Prompt Optimization`)
OpenAI provee la herramienta [Prompt Optimizer](https://platform.openai.com/chat/edit?models=gpt-5&optimize=true) para estructurar y adaptar instrucciones específicamente al estilo de razonamiento de GPT-5.

---

### 9. Guía de Migración hacia la Familia GPT-5

OpenAI recomienda actualizar aplicaciones existentes a los nuevos modelos de la familia GPT-5:

| Modelo Anterior | Modelo GPT-5 Recomendado | Nivel de Razonamiento Inicial | Notas de Migración |
| :--- | :--- | :--- | :--- |
| **o3** | **GPT-5** | `medium` | Iniciar en `medium` con afinamiento de prompt; aumentar a `high` si se requiere. |
| **gpt-4.1** | **GPT-5** | `minimal` | Iniciar en `minimal`; aumentar a `low` para mayor precisión analítica. |
| **o4-mini** | **GPT-5-mini** | `medium` | Usar GPT-5-mini con optimización de prompt. |
| **gpt-4.1-mini** | **GPT-5-mini** | `minimal` | Sustitución directa de bajo costo y baja latencia. |
| **gpt-4.1-nano** | **GPT-5-nano** | `minimal` | Para tareas de clasificación ultrarrápida al borde o gran escala. |

---

## Ejecución del Jupyter Notebook

Para explorar de manera visual e interactiva todos los ejemplos:

```bash
jupyter notebook notebooks/gpt_5_api_tutorial.ipynb
```
