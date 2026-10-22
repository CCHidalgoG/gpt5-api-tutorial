import os
import random
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_sql_query(sql: str) -> str:
    """Simulador de base de datos SQL local."""
    print(f"\n[BD SIMULADA] Ejecutando SQL recibido en texto plano:\n{sql}\n")
    categories = ["Electronics", "Clothing", "Furniture", "Toys", "Books"]
    result = "category   | total_sales\n" + "-" * 28 + "\n"
    for cat in categories:
        result += f"{cat:<11} | {random.randint(5000, 200000)}\n"
    return result


def run_freeform_input_demo():
    print("=== Custom Tools con Entrada Libre (Freeform Text / SQL) ===")

    # Herramienta personalizada de tipo 'custom' que acepta texto plano directamente
    tools = [
        {
            "type": "custom",
            "name": "sql_query_runner",
            "description": "Runs raw SQL queries on the company sales database.",
        }
    ]

    messages = [
        {
            "role": "user",
            "content": "Show me the total sales for each product category last month.",
        }
    ]

    # 1) Primera llamada: el modelo emite la llamada con texto libre en 'input'
    print("\n1) Enviando solicitud al modelo...")
    resp = client.responses.create(model="gpt-5", tools=tools, input=messages)

    # Conservar la salida en el historial para mantener el call_id
    messages += resp.output

    # Identificar el tool call generado
    tool_call = next(
        (
            x
            for x in resp.output
            if getattr(x, "type", "") in ("custom_tool_call", "function_call", "tool_call")
        ),
        None,
    )
    if not tool_call:
        print("No se generó tool call. Salida:", resp.output_text)
        return

    # Extraer el texto libre (campo 'input')
    raw_text = getattr(tool_call, "input", None) or getattr(tool_call, "arguments", "")
    sql_text = raw_text.strip()
    print(f"Tool Call Name: {getattr(tool_call, 'name', 'N/A')}")
    print(f"SQL Generado por GPT-5:\n{sql_text}")

    # 2) Ejecutar la herramienta localmente
    fake_result = run_sql_query(sql_text)

    # 3) Enviar el resultado de vuelta al modelo con el mismo call_id
    messages.append(
        {
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": fake_result,
        }
    )

    # 4) Segunda llamada: el modelo convierte la respuesta estructurada en lenguaje natural
    print("2) Solicitando interpretación final en lenguaje natural...")
    final = client.responses.create(model="gpt-5", tools=tools, input=messages)
    print("\nRespuesta Final:")
    print(final.output_text)


if __name__ == "__main__":
    run_freeform_input_demo()
