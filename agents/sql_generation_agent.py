import os
import sys

sys.path.append(os.path.abspath("../"))

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

from State_Schema.state_schema import AgentState
from State_Schema.schema_info import SCHEMA_INFO



llm = ChatOllama(model = "qwen3:8b")

prompt=f"""
You are an expert SQL query generator from natural language query. Convert the following natural language query into valid SQL query.

SCHEM_INFO:\n\n{SCHEMA_INFO}

Important Guidelines:
- Use only the tables and columns mentioned in the schema.
- Use proper JOIN clauses when querying multiple tables.
- Return only SQL query without any explaination or markdown formatting.
- If question contains multiple sub-questions, generate separate SQL queries separated by semicolons.
- Use aggregate functions (like COUNT, SUM, AVG etc) appropriately
- Add "LIMIT" clauses for queries that might return many rows (default limit 10 unless user specifies).
- Use proper WHERE clauses to filter data.
- For date comparisions, remember dates are stored as text not in ISO format.
- Each SQL statement should be in its own line for clarity when multiple queries are needed. 
"""

sql_generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            prompt
        ),
        MessagesPlaceholder(variable_name="question")
    ]
)

chain = sql_generation_prompt | llm


def sql_agent(state: AgentState):
    """generate sql query from the natural language"""

    # output = chain.invoke({"question": [HumanMessage(content=question)]})
    output = chain.invoke(state["question"])

    # print(output.content)
    return output.content


if __name__ == "__main__":
    initial_state = {"question": "what are the top 5 states by number of customers?"}

    query=sql_agent(initial_state)

    import sqlite3

    conn = sqlite3.connect("../ecommerce.db")
    cursor = conn.cursor()

    print(query)

    cursor.execute(query)
    print(cursor.fetchall())