import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_cot_handoff_demo():
    print("=== Turno 1: Pregunta inicial con bajo razonamiento ===")
    first = client.responses.create(
        model="gpt-5",
        input="¿Quién es el padre de Python?",
        reasoning={"effort": "minimal"},
        text={"verbosity": "low"},
    )
    print("Respuesta Turno 1:")
    print(first.output_text)
    print(f"ID del turno 1: {first.id}")

    print("\n" + "=" * 50 + "\n")

    print("=== Turno 2: Seguimiento pasando previous_response_id (CoT Handoff) ===")
    # Se encadena la conversación pasando previous_response_id sin repetir el sujeto
    followup = client.responses.create(
        model="gpt-5",
        previous_response_id=first.id,
        input="Escribe una breve publicación para un blog sobre su legado y trayectoria.",
        reasoning={"effort": "medium"},
        text={"verbosity": "high"},
    )
    print("Respuesta Turno 2 (mantiene el contexto y cadena de razonamiento):")
    print(followup.output_text)


if __name__ == "__main__":
    run_cot_handoff_demo()
