"""
Writing agent for academic writing workflow
"""
from typing import Dict
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def create_writer():
    """Create the writing agent."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an academic writing assistant. Write according to the current step."),
        ("user", "Writing task: {prompt}\nCurrent step: {current_step}\nExisting text: {text}")
    ])
    
    model = ChatOpenAI(temperature=0.7)
    
    def write(state: Dict) -> Dict:
        """Generate text for current step."""
        # Get current step
        current_step = state["steps"][state["current_step_index"]]
        
        # Get response from model
        response = model.invoke(prompt.format_messages(
            prompt=state["prompt"],
            current_step=current_step,
            text=state["text"]
        ))
        
        # Update text
        state["text"] += "\n\n" + response.content
        
        # Update progress
        state["current_step_index"] += 1
        if state["current_step_index"] >= len(state["steps"]):
            state["done"] = True
            state["needs_editing"] = True
            
        return state
        
    return write
