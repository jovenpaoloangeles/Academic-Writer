"""
Main script for academic writing workflow using LangGraph
"""
from typing import Dict
from langgraph.graph import Graph, StateGraph, END
from modules.state import AgentState
from modules.agents.planner import create_planner
from modules.agents.writer import create_writer
from modules.agents.editor import create_editor
from modules.utils import save_to_docx, save_to_bib

def should_continue(state: AgentState) -> str:
    """Determine whether to continue writing, edit, or end."""
    if not state["done"]:
        return "continue"
    elif state["needs_editing"]:
        return "edit"
    return "editor"  # Always go through editor before ending

def create_graph() -> Graph:
    """Create the writing workflow graph."""
    
    # Create workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", create_planner())
    workflow.add_node("writer", create_writer())
    workflow.add_node("editor", create_editor())
    
    # Add edges
    workflow.add_edge('planner', 'writer')
    workflow.add_conditional_edges(
        'writer',
        should_continue,
        {
            "continue": "writer",
            "edit": "editor",
            "editor": "editor"
        }
    )
    
    # Add edge from editor to end
    workflow.add_edge('editor', END)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    return workflow.compile()

def process_writing_task(prompt: str) -> tuple[str, str, str]:
    """Process a writing task from start to finish."""
    
    # Initialize state
    state = {
        "messages": [],
        "prompt": prompt,
        "plan": None,
        "text": "",
        "edited_text": None,
        "next_step": None,
        "steps": [],
        "current_step_index": 0,
        "done": False,
        "needs_editing": False
    }
    
    # Create and run graph
    graph = create_graph()
    result = graph.invoke(state)
    
    # Save outputs
    docx_file = save_to_docx(result, prompt)
    bib_file = save_to_bib(result, prompt)
    
    # Return edited text if available, otherwise original text
    text = result["edited_text"] if result["edited_text"] else result["text"]
    return text, docx_file, bib_file

if __name__ == "__main__":
    # Example usage
    prompt = """Write a comprehensive review paper on Acid-Treated Philippine Natural Zeolites for Nitrogen Wastewater Mitigation."""
    
    result, docx_file, bib_file = process_writing_task(prompt)
    print("\nFinal Text saved to:", docx_file)
    if bib_file:
        print("References saved to:", bib_file)
    print("\nFirst few lines of text:\n")
    print("\n".join(result.split("\n")[:10]))  # Print first 10 lines
