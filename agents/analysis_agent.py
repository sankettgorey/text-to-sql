"""
this agent converts raw SQL JSON output into user understandable and readable format using AI
"""
import os
import sys
sys.path.append(os.path.abspath("../"))

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from State_Schema.state_schema import AgentState

llm = ChatOllama(model="qwen3:8b")


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant who explains database query results into natural language."
            "Please provide clear and concise answer to the original question based on query result. Format the answer in a user-friendly way."
            "If result contains numbers, present them clearely."
            "If there are multiple queries/results for multi-part questions, address each part of the question separately."
            "Use bullet points or numbered lists for multiple answers"
        ),
        (
            "human",
            "Question: {question}"
            "sql_query: {sql_query}"
            "query_result: {query_result}"
        )
    ]
)

chain = prompt | llm


def analysis_agent(state: AgentState):
    
    final_answer = chain.invoke(
        {
            "question": state["question"],
            "sql_query": state["sql_query"],
            "query_result": state["query_result"]
        }
    )

    state["final_answer"] = final_answer.content

    return state


if __name__ == "__main__":
    result = {'sql_query': 'SELECT customer_state, COUNT(*) AS num_customers\nFROM customers\nGROUP BY customer_state\nORDER BY num_customers DESC\nLIMIT 5', 
              'query_result': '[\n    {\n        "customer_state": "SP",\n        "num_customers": 41746\n    },\n    {\n        "customer_state": "RJ",\n        "num_customers": 12852\n    },\n    {\n        "customer_state": "MG",\n        "num_customers": 11635\n    },\n    {\n        "customer_state": "RS",\n        "num_customers": 5466\n    },\n    {\n        "customer_state": "PR",\n        "num_customers": 5045\n    }\n]', "question": "what are the top 5 states by number of customers?"}

    output = analysis_agent(result)
    print(output)
    print()
    print(output["final_answer"])