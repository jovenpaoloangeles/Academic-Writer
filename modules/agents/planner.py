"""
Planning agent for academic writing workflow
"""
from typing import Dict
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def create_planner():
    """Create the planning agent."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a research paper planning assistant. Create a detailed outline."),
        ("user", "{input}")
    ])
    
    model = ChatOpenAI(temperature=0.7)
    
    def plan(state: Dict) -> Dict:
        """Generate a writing plan."""
        # Get response from model
        response = model.invoke(prompt.format_messages(input=state["prompt"]))
        
        # Parse response into steps
        steps = [step.strip() for step in response.content.split('\n') if step.strip()]
        
        # Update state
        state["plan"] = steps
        state["steps"] = steps
        state["current_step_index"] = 0
        
        return state
        
    return plan
