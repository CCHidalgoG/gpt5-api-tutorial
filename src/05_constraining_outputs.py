import os
import random
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_sql_query(sql: str) -> str:
    """Simulador de base de datos SQL con datos sintéticos."""
    cats = ["Electronics", "Clothing", "Furniture", "Toys", "Books"]
    rows = [f"{c:<11} | {random.randint(5_000, 200_000)}" for c in cats]
    return "category   | total_sales\n" + "-" * 28 + "\n" + "\n".join(rows)


def run_grammar_constraint_demo():
    print("=== Restricción de Salidas con Gramáticas Libres de Contexto (CFG / Lark) ===")

    # Definición de la gramática Lark para restringir sintácticamente la consulta SQL generada
    lark_grammar = r"""
start: SELECT CATEGORY COMMA SUM LPAREN SALES RPAREN AS TOTAL_SALES FROM ORDERS WHERE ORDER_MONTH EQ ESCAPED_STRING GROUP BY CATEGORY ORDER BY TOTAL_SALES (DESC|ASC)?

SELECT: "SELECT"
CATEGORY: "category"
COMMA: ","
SUM: "SUM"
LPAREN: "("
SALES: "sales"
RPAREN: ")"
AS: "AS"
TOTAL_SALES: "total_sales"
FROM: "FROM"
ORDERS: "orders"
WHERE: "WHERE"
ORDER_MONTH: "order_month"
EQ: "="
GROUP: "GROUP"
BY: "BY"
ORDER: "ORDER"
DESC: "DESC"
ASC: "ASC"

%import common.ESCAPED_STRING
%ignore /[ \t\r\n]+/
"""

    tools = [
        {
            "type": "custom",
            "name": "sql_query_runner",
            "description": "Runs raw SQL on the sales DB.",
            "format": {
                "type": "grammar",
                "syntax": "lark",
                "definition": lark_grammar,
            },
        }
    ]

    msgs = [
        {
            "role": "user",
            "content": "Show me the total sales for each product category last month.",
        }
    ]

    print("\n1) Solicitando llamada con formato gobernado por gramática...")
    resp = client.responses.create(
        model="gpt-5", input=msgs, tools=tools, text={"format": {"type": "text"}}
    )
    print("Objetos crudos devueltos:")
    for item in resp.output:
        print(" ", item)

    msgs += resp.output
    tool_call = next(
        x
        for x in resp.output
        if getattr(x, "type", "") in ("custom_tool_call", "function_call", "tool_call")
    )
    sql = (getattr(tool_call, "input", None) or getattr(tool_call, "arguments", "")).strip()
    print(f"\nConsulta SQL extraída (100% conforme a la gramática):\n{sql}")

    print("\n2) Ejecución de la consulta localmente...")
    tool_result = run_sql_query(sql)
    print(tool_result)

    msgs.append(
        {
            "type": "function_call_output",
            "call_id": getattr(tool_call, "call_id", None) or tool_call["call_id"],
            "output": tool_result,
        }
    )

    print("\n3) Segunda llamada para respuesta final en lenguaje natural...")
    final = client.responses.create(
        model="gpt-5", input=msgs, tools=tools, text={"format": {"type": "text"}}
    )
    print("\nRespuesta natural final:")
    print(final.output_text)


if __name__ == "__main__":
    run_grammar_constraint_demo()
