
from typing import Dict, Any, Optional
from pydantic import BaseModel


class StartSimulationRequest(BaseModel):
    industry: str
    role: str


class StartSimulationResponse(BaseModel):
    session_id: int
    initial_state: Dict[str, Any]


class SimulationActionRequest(BaseModel):
    action_id: str
    choice: str


class SimulationActionResponse(BaseModel):
    new_state: Dict[str, Any]
    feedback: str


class EndSimulationResponse(BaseModel):
    final_state: Dict[str, Any]
    score: Dict[str, Any]
    coach_summary: str