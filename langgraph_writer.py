import os
from typing import Annotated, Sequence, TypedDict, Required, Union
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import Graph, StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import json
from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# State definitions
class AgentState(TypedDict):
    """State for the writing agents."""
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    prompt: Annotated[str, "The original writing prompt"]
    plan: Annotated[Union[str, None], "The writing plan"]
    text: Annotated[str, "The generated text"]
    edited_text: Annotated[Union[str, None], "The edited text"]
    next_step: Annotated[Union[str, None], "The next step to execute"]
    steps: Annotated[list[str], "List of all steps"]
    current_step_index: Annotated[int, "Index of current step"]
    done: Annotated[bool, "Whether the writing is complete"]
    needs_editing: Annotated[bool, "Whether the text needs editing"]

def get_response_gpt4(prompt: str, max_new_tokens: int = 16384 , temperature: float = 0.7, stop=None) -> str:
    """Get response from GPT-4 with retry logic."""
    tries = 0
    while tries < 10:
        tries += 1
        try:
            headers = {
                'Authorization': f"Bearer {OPENAI_API_KEY}",
            }
            messages = [
                {'role': 'user', 'content': prompt},
            ]
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions", 
                json={
                    "model": "gpt-4o",
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_new_tokens,
                    "stop": stop,
                }, 
                headers=headers, 
                timeout=600
            )
            if resp.status_code != 200:
                raise Exception(resp.text)
            resp = resp.json()
            break
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            if "maximum context length" in str(e):
                raise e
            elif "triggering" in str(e):
                return 'Trigger OpenAI\'s content management policy'
            print(f"Error Occurs: \"{str(e)}\"        Retry ...")
    else:
        print("Max tries. Failed.")
        return "Max tries. Failed."
    try:
        return resp["choices"][0]["message"]["content"]
    except: 
        return ''

# Load prompt templates
with open('prompts/plan.txt', 'r', encoding='utf-8') as f:
    PLAN_TEMPLATE = f.read()

with open('prompts/write.txt', 'r', encoding='utf-8') as f:
    WRITE_TEMPLATE = f.read()

with open('prompts/edit.txt', 'r', encoding='utf-8') as f:
    EDIT_TEMPLATE = f.read()

def create_planner():
    """Create the planner agent that breaks down the writing task."""
    
    def planner(state: AgentState) -> AgentState:
        # Get response using the same method as original implementation
        response = get_response_gpt4(
            PLAN_TEMPLATE.replace('$INST$', state['prompt'])
        )
        
        # Parse steps from plan
        steps = [line.strip() for line in response.split('\n') if line.strip()]
        
        # Update state
        return {
            **state,
            "plan": response,
            "steps": steps,
            "next_step": steps[0] if steps else None,
            "current_step_index": 0,
            "done": False,
            "needs_editing": False
        }
    
    return planner

def create_writer():
    """Create the writer agent that executes each step of the plan."""
    
    def writer(state: AgentState) -> AgentState:
        if not state["next_step"]:
            return {**state, "done": True, "needs_editing": True}
            
        # Format prompt
        prompt = WRITE_TEMPLATE.replace('$INST$', state['prompt']) \
                              .replace('$PLAN$', state['plan']) \
                              .replace('$TEXT$', state['text']) \
                              .replace('$STEP$', state['next_step'])
        
        # Get response using the same method as original implementation
        new_text = get_response_gpt4(prompt)
        
        # Update text with new paragraph
        updated_text = state['text']
        if updated_text:
            updated_text += "\n\n"
        updated_text += new_text
        
        # Move to next step
        next_index = state['current_step_index'] + 1
        next_step = state['steps'][next_index] if next_index < len(state['steps']) else None
        
        # Update state
        return {
            **state,
            "text": updated_text,
            "next_step": next_step,
            "current_step_index": next_index,
            "done": next_step is None,
            "needs_editing": next_step is None  # Set needs_editing when done
        }
    
    return writer

def create_editor():
    """Create the editor agent that reviews and adds citation markers."""
    
    def editor(state: AgentState) -> AgentState:
        if not state["needs_editing"]:
            return state
            
        # Format prompt
        prompt = EDIT_TEMPLATE.replace('$TEXT$', state['text'])
        
        # Get response
        edited_text = get_response_gpt4(prompt)
        
        # Update state
        return {
            **state,
            "edited_text": edited_text,
            "needs_editing": False
        }
    
    return editor

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

def process_writing_task(prompt: str) -> str:
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
    
    # Return edited text if available, otherwise original text
    return result["edited_text"] if result["edited_text"] else result["text"]

if __name__ == "__main__":
    # Example usage
    prompt = """Write a 10000-word for Bayesian Optimization Framework for Accelerated Nanoparticle Synthesis"""
    
    result = process_writing_task(prompt)
    print("\nFinal Text:\n")
    print(result)
