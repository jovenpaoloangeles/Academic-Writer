"""
Editing agent for academic writing workflow
"""
from typing import Dict
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def create_editor():
    """Create the editing agent."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an academic editor. Improve the writing while maintaining accuracy."),
        ("user", "Please edit this text:\n{text}")
    ])
    
    model = ChatOpenAI(temperature=0.7)
    
    def edit(state: Dict) -> Dict:
        """Edit the complete text."""
        # Get response from model
        response = model.invoke(prompt.format_messages(text=state["text"]))
        
        # Update state
        state["edited_text"] = response.content
        state["needs_editing"] = False
        
        return state
        
    return edit
