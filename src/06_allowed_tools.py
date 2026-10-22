import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_allowed_tools_demo():
    print("=== Subconjunto de Herramientas Permitidas (allowed_tools) ===")

    # Conjunto completo de herramientas disponibles (N = 2)
    tools = [
        {
            "type": "function",
            "name": "get_weather",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
        {
            "type": "function",
            "name": "send_email",
            "parameters": {
                "type": "object",
                "properties": {"to": {"type": "string"}, "body": {"type": "string"}},
                "required": ["to", "body"],
            },
        },
    ]

    # Restringir a un subconjunto permitido (M < N) con mode="required"
    print("Enviando prompt con tool_choice restringido a 'get_weather' (mode='required')...")
    resp = client.responses.create(
        model="gpt-5",
        input="What's the weather in Oslo?",
        tools=tools,
        tool_choice={
            "type": "allowed_tools",
            "mode": "required",  # O "auto" para permitir al modelo decidir dentro del subconjunto
            "tools": [{"type": "function", "name": "get_weather"}],
        },
    )

    print("\nLlamadas a herramientas detectadas en la respuesta:")
    for item in resp.output:
        if getattr(item, "type", None) in ("function_call", "tool_call", "custom_tool_call"):
            print("  - Tool Name:", getattr(item, "name", None))
            print("  - Arguments:", getattr(item, "arguments", None))


if __name__ == "__main__":
    run_allowed_tools_demo()
