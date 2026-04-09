from typing import Annotated

from langgraph.graph.message import add_messages
from pydantic import BaseModel

from app.models.research import ResearchRequest, ResearchResult


class AgentState(BaseModel):
    request: ResearchRequest
    result: ResearchResult
    messages: Annotated[list, add_messages] = []
    current_step: str = "start"
    error: str | None = None

    class Config:
        arbitrary_types_allowed = True