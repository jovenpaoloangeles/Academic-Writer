"""
State management for the academic writing workflow
"""
from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    """Type definition for agent state."""
    messages: List[str]
    prompt: str
    plan: Optional[List[str]]
    text: str
    edited_text: Optional[str]
    next_step: Optional[str]
    steps: List[str]
    current_step_index: int
    done: bool
    needs_editing: bool
