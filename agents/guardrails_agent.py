from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

from State_Schema.state_schema import AgentState
from pydantic import BaseModel, Field
import os
import sys

sys.path.append(os.path.abspath(".."))




class FormattedResponse(BaseModel):
    is_in_scope: bool = Field(..., description="whether the asked question is related to the e-commerce db. If yes it will be in scope otherwise it will be out-of-scope")
    is_greeting: bool = Field(..., description="whether question is a casual greeting")
    reason: str = Field(..., description="reason why it is in or isn't scope or if it's greeting")


llm = ChatOllama(model="qwen3:8b")

llm_with_structured_output = llm.with_structured_output(FormattedResponse)

system_prompt = """
    You are a guardrails system for an e-commerce database chatbot. Your job is to determine if user's question is related to e-commerce data, if it's greeting, if it's out of scope.


    The chatbot has access to e-commerce database wit the information about:
    - Customers and their locations.
    - Order and order status (data from 2016-2018)
    - Products and categories
    - Sellers
    - Payments
    - Reviews
    - Shipping and delivery information


    Examples of grerting messages:
    - "Hi", "Hello", "hey"
    - "Good Morning", "Good Evening"
    - Any casual greeting or introduction

    Examples of out-of scope information
    - Personal questions (e.g., "What is my wife's name?", "Where do I live?")
    - Political questions (e.g., "Who should I vote for?", "What do you think about the president?")
    - General knowledge (e.g., "What is the capital of France?", "How does photosynthesis work?")
    - Unrelated topics (e.g., "Tell me a joke", "What's the weather like?")

    If the question is a greeting, mark is_greeting as true and is_in_scope as false.
    If the question is ambiguous but could potentially relate to the e-commerce data, mark it as in_scope.

    Respond strictly in JSON matching the given schema.
    """

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            system_prompt
        ),
        MessagesPlaceholder(variable_name="question")
    ]
)

guardrails_chain = prompt | llm_with_structured_output


def guardrails_agent(state: AgentState):

    

    output = guardrails_chain.invoke(
        {
            "question": [HumanMessage(content=state["question"])]
        }
    )

    is_greeting = output.is_greeting

    if is_greeting:
        state["final_answer"] = """Hi there! I am e-commerce assistant. I can answer all the queries related to orders, customers, products, sellers, payments, and reviews between 2016-2018. How can I help you today?"
        """
        return state
    
    if output.is_in_scope:
        state["final_answer"] = "I apologize, but your question appears to be out of scope. I can only answer questions about the e-commerce data, including:\n\n- Customer information and locations\n- Orders and order status\n- Products and categories\n- Sellers and their performance\n- Payment information\n- Reviews and ratings\n- Shipping and delivery data\n\nPlease ask a question related to the e-commerce database."
    
        return state


if __name__ == "__main__":

    state = {
        "question": "can you tell me where is Pune?"
    }

    guardrails_agent(state)