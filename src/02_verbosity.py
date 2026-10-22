import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_verbosity_demo():
    prompt = "¿Quién es Guido van Rossum y cuál es su contribución al software?"

    print("=== 1) Verbosity: LOW (Respuesta concisa) ===")
    resp_low = client.responses.create(
        model="gpt-5",
        input=prompt,
        reasoning={"effort": "minimal"},
        text={"verbosity": "low"},
    )
    print("Respuesta Low:")
    print(resp_low.output_text)

    print("\n" + "=" * 50 + "\n")

    print("=== 2) Verbosity: HIGH (Explicación detallada y contextualizada) ===")
    resp_high = client.responses.create(
        model="gpt-5",
        input=prompt,
        reasoning={"effort": "minimal"},
        text={"verbosity": "high"},
    )
    print("Respuesta High:")
    print(resp_high.output_text)


if __name__ == "__main__":
    run_verbosity_demo()
