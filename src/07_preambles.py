import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_weather(city: str):
    return {"city": city, "temperature_c": 12, "condition": "Partly Cloudy"}


def run_preambles_demo():
    print("=== Preámbulos en Tool Calling (Preambles) ===")

    tools = [
        {
            "type": "function",
            "name": "get_weather",
            "description": "Get current temperature and conditions for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
                "additionalProperties": False,
            },
            "strict": True,
        }
    ]

    msgs = [
        {
            "role": "system",
            "content": (
                "Before you call a tool, explain why you are calling it in "
                "ONE short sentence prefixed with 'Preamble:'."
            ),
        },
        {"role": "user", "content": "What's the weather in Oslo?"},
    ]

    # 1) Primera llamada: se espera el preámbulo visible + la llamada a la herramienta
    print("1) Realizando primera llamada (esperando preámbulo y tool call)...")
    resp = client.responses.create(model="gpt-5", input=msgs, tools=tools)

    print("\n--- Objetos de la primera respuesta ---")
    for item in resp.output:
        t = getattr(item, "type", None)
        if t == "message":
            print("PREÁMBULO:", getattr(item, "content", None))
        if t in ("function_call", "tool_call", "custom_tool_call"):
            print("HERRAMIENTA:", getattr(item, "name", None))
            print("ARGUMENTOS:", getattr(item, "arguments", None))

    tool_call = next(
        x
        for x in resp.output
        if getattr(x, "type", None) in ("function_call", "tool_call", "custom_tool_call")
    )
    msgs += resp.output  # Mantener contexto

    # 2) Ejecutar herramienta localmente
    args = json.loads(getattr(tool_call, "arguments", "{}"))
    city = args.get("city", "Oslo")
    tool_result = get_weather(city)

    # 3) Devolver el resultado de la herramienta
    msgs.append(
        {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": json.dumps(tool_result),
        }
    )

    # 4) Llamada final al modelo
    print("\n2) Realizando llamada final con el resultado de la herramienta...")
    final = client.responses.create(model="gpt-5", input=msgs, tools=tools)
    print("\n--- Respuesta Final ---")
    print(final.output_text)


if __name__ == "__main__":
    run_preambles_demo()
