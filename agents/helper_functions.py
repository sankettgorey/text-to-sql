"""
decides whether to retry SQL query generation based on the error and iteration counter
"""


import os
import sys
sys.path.append(os.path.abspath("../"))
import json

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from State_Schema.state_schema import AgentState

import pandas as pd
from pydantic import BaseModel, Field

llm = ChatOllama(model="qwen3:8b")



def should_retry(state: AgentState):
    """decides whether to retry SQL query generation based on the error and iteration counter"""

    if state.get("error"):
        iteration = state.get("iteraion", 0)

        if iteration < 3:
            return "retry"
        else:
            return "end"

    return "success"


def should_generate_graph(state: AgentState):
    """decides whether to generate graph"""

    if state.get("needs_graph", False):
        return "visualize_agent"

    return "skip_graph"



def check_scope(state: AgentState):
    """checks whether question asked by user is in scope or out of scope"""

    if state.get("is_in_scope", False):
        return "in_scope"
    return "out_of_scope"

