from langgraph.graph import START, END, StateGraph


from State_Schema.state_schema import AgentState
from agents.sql_generation_agent import sql_agent
from agents.visualization_agent import visualization_agent
from agents.helper_functions import should_generate_graph, should_retry, check_scope
from agents.analysis_agent import analysis_agent
from agents.decide_graph_need import decide_graph_need
from agents.execute_sql_query_agent import execute_query
from agents.error_agent import error_agent
from agents.guardrails_agent import guardrails_agent


def create_text2sql_agent():
    """
    defines all nodes and edges and creates langgraph graph 
    """

    graph = StateGraph(AgentState)

    graph.add_node("guardrails_agent", guardrails_agent)
    graph.add_node("sql_query_generation_agent", sql_agent)
    graph.add_node("execute_query", execute_query)
    graph.add_node("error", error_agent)
    graph.add_node("visualize_agent", visualization_agent)
    graph.add_node("analysis_agent", analysis_agent)
    graph.add_node("decide_graph_need", decide_graph_need)


    graph.set_entry_point("sql_query_generation_agent")

    # graph.add_conditional_edges(
    #     "guardrails_agent",
    #     check_scope,
    #     {
    #         "in_scope": "sql_query_generation_agent",
    #         "out_of_scope": END
    #     }
    # )
    graph.add_edge("sql_query_generation_agent", "execute_query")
    graph.add_conditional_edges(
        "execute_query",
        should_retry,
        {
            "success": "analysis_agent",
            "retry": "error",
        }
    )

    graph.add_edge("error", "execute_query")

    graph.add_edge(
        "analysis_agent",
        "decide_graph_need"
    )

    graph.add_conditional_edges(
        "decide_graph_need",
        should_generate_graph,
        {
            "visualize_agent": "visualize_agent",
            "skip_graph": END
        }
    )

    graph.add_edge("visualize_agent", END)

    return graph.compile()


def generate_graph_visualization(output_path="text2sql_workflow.png"):
    """
    Generate a PNG visualization of the LangGraph workflow.
    
    Args:
        output_path: Path where the PNG file will be saved (default: "text2sql_workflow.png")
    
    Returns:
        str: Path to the generated PNG file
    """
    try:
        # Get the graph visualization
        graph_image = create_text2sql_agent().get_graph().draw_mermaid_png()
        
        # Save to file
        with open(output_path, "wb") as f:
            f.write(graph_image)
        
        print(f"Graph visualization saved to: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error generating graph visualization: {e}")
        print("Make sure you have 'pygraphviz' or 'grandalf' installed:")
        print("  pip install pygraphviz")
        print("  or")
        print("  pip install grandalf")
        return None
    




async def process_question_stream(question: str):
    """
    Process a natural language question and stream node execution events.
    This is an async generator that yields node events for debugging visualization.
    
    Yields:
        dict: Event with type ('node_start', 'node_end', 'error', 'final') and data
    """

    from langchain_core.messages import HumanMessage

    # question = 

    create_text2sql_graph = create_text2sql_agent()
    initial_state = AgentState(
        question=[HumanMessage(content=question)],
        sql_query="",
        query_result="",
        final_answer="",
        error="",
        iteration=0,
        needs_graph=False,
        graph_type="",
        graph_json="",
        is_in_scope=True
    )
    
    current_state = initial_state.copy()
    
    try:
        # Stream events from the graph
        async for event in create_text2sql_graph.astream_events(
            initial_state,
            config={"recursion_limit": 50},
            version="v1"
        ):
            event_type = event.get("event")
            
            # Node start event
            if event_type == "on_chain_start":
                node_name = event.get("name", "")
                if node_name in ["sql_agent", "execute_sql", "analysis_agent", 
                               "error_agent", "decide_graph_need", "viz_agent"]:
                    yield {
                        "type": "node_start",
                        "node": node_name,
                        "input": current_state
                    }
            
            # Node end event
            elif event_type == "on_chain_end":
                node_name = event.get("name", "")
                if node_name in ["sql_agent", "execute_sql", "analysis_agent", 
                               "error_agent", "decide_graph_need", "viz_agent"]:
                    output = event.get("data", {}).get("output", {})
                    if output:
                        current_state.update(output)
                        yield {
                            "type": "node_end",
                            "node": node_name,
                            "output": output,
                            "state": current_state.copy()
                        }
        
        # Send final result
        yield {
            "type": "final",
            "result": current_state
        }
        
    except Exception as e:
        yield {
            "type": "error",
            "error": str(e)
        }
    


if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    # generate_graph_visualization()

    workflow = create_text2sql_agent()

    output = workflow.invoke(
        {
            "question": [HumanMessage("what are the top 5 states by number of customers?")],
            "error": "",
            "iteration": 0
        }
    )

    print(output)

