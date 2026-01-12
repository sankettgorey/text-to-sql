"""
based on the question and query_result, this agent decides whether adding graph for the answer adds a value
"""

import os
import sys
sys.path.append(os.path.abspath("../"))

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from State_Schema.state_schema import AgentState

from pydantic import BaseModel, Field

from typing import Literal

llm = ChatOllama(model="qwen3:8b")



prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Analyse the given question and query result to determine if visualization would be useful."
            "Respond 'True/False' for needs_graph and respond from these: 'bar/line/pie/scatter/none' for 'graph_type'"
        ),
        (
            "human",
            "Question: {question}"
            "query_result: {query_result}"
        )

    ]
)

class DecideGraphType(BaseModel):

    needs_graph: bool = Field(..., description="Decision whether graph needs to be plotted to add more value")
    graph_type: Literal["bar", "pie", "scatter", "line", "none"] = Field(..., description="name of the graph to be plotted")

structured_llm = llm.with_structured_output(DecideGraphType)

chain = prompt | structured_llm

def decide_graph_need(state: AgentState):
    """
    decides if graph visualization would be helpful for the query
    """

    query_result = state["query_result"]

    if not query_result or query_result == "No Results Found" or state.get("error"):
        state["needs_graph"] = False
        state["graph_type"] = ""
        state["graph_json"] = ""
        
        return state
    
    output = chain.invoke(
        {
            "question": state["question"],
            "query_result": state["query_result"]
        }
    )

    state["needs_graph"] = output.needs_graph
    state["graph_type"] = output.graph_type

    return state


if __name__ == "__main__":
    initial_state = {"question": "what are the top 5 states by number of customers?",
                     'query_result': '[\n    {\n        "customer_state": "SP",\n        "num_customers": 41746\n    },\n    {\n        "customer_state": "RJ",\n        "num_customers": 12852\n    },\n    {\n        "customer_state": "MG",\n        "num_customers": 11635\n    },\n    {\n        "customer_state": "RS",\n        "num_customers": 5466\n    },\n    {\n        "customer_state": "PR",\n        "num_customers": 5045\n    }\n]'
    }
    decide_graph_need(initial_state)