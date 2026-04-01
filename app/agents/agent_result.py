"""
Shared response shape for specialist agents and the coordinator.
"""
from pydantic import BaseModel, Field


class AgentTraceStep(BaseModel):
    stage: str
    agent: str
    detail: str


class AgentExecutionResult(BaseModel):
    reply: str
    agent_name: str
    agent_display_name: str
    handoff_trace: list[AgentTraceStep] = Field(default_factory=list)
