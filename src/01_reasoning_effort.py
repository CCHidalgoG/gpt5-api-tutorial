import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar variables de entorno desde .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_reasoning_demo():
    prompt = "¿Quién es el creador de Python y en qué año se lanzó?"

    print("=== 1) Reasoning Effort: MINIMAL ===")
    resp_minimal = client.responses.create(
        model="gpt-5",
        input=prompt,
        reasoning={"effort": "minimal"},
    )
    print("Respuesta:")
    print(resp_minimal.output_text)
    print("\nUso de Tokens (Minimal):")
    print(f"  - Input tokens: {resp_minimal.usage.input_tokens}")
    print(f"    - Cached tokens: {resp_minimal.usage.input_tokens_details.cached_tokens}")
    print(f"  - Output tokens: {resp_minimal.usage.output_tokens}")
    print(f"    - Reasoning tokens: {resp_minimal.usage.output_tokens_details.reasoning_tokens}")
    print(f"  - Total tokens: {resp_minimal.usage.total_tokens}")

    print("\n" + "=" * 50 + "\n")

    print("=== 2) Reasoning Effort: HIGH ===")
    resp_high = client.responses.create(
        model="gpt-5",
        input=prompt,
        reasoning={"effort": "high"},
    )
    print("Respuesta:")
    print(resp_high.output_text)
    print("\nUso de Tokens (High):")
    print(f"  - Input tokens: {resp_high.usage.input_tokens}")
    print(f"    - Cached tokens: {resp_high.usage.input_tokens_details.cached_tokens}")
    print(f"  - Output tokens: {resp_high.usage.output_tokens}")
    print(f"    - Reasoning tokens: {resp_high.usage.output_tokens_details.reasoning_tokens}")
    print(f"  - Total tokens: {resp_high.usage.total_tokens}")


if __name__ == "__main__":
    run_reasoning_demo()
