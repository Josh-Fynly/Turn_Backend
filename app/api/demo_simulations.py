from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.services.simulation_engine import (
    load_simulation,
    initialize_state,
    apply_action,
    generate_score,
    generate_coach_summary,
)

router = APIRouter(prefix="/demo/simulations", tags=["Demo Simulations"])


# -------------------------
# Request Schemas
# -------------------------

class ActionRequest(BaseModel):
    state: Dict[str, Any]
    action_id: str
    choice: str


class StateRequest(BaseModel):
    state: Dict[str, Any]


# -------------------------
# Endpoints
# -------------------------

@router.get("/{simulation_id}")
def start_simulation(simulation_id: str):
    """
    Load simulation scenario and initialize state.
    """
    try:
        scenario = load_simulation(simulation_id)
        state = initialize_state(scenario)

        return {
            "simulation_id": simulation_id,
            "meta": scenario.get("meta", {}),
            "context": scenario.get("context", {}),
            "actions": scenario.get("actions", {}),
            "state": state,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{simulation_id}/act")
def take_action(simulation_id: str, payload: ActionRequest):
    """
    Apply a user decision.
    """
    try:
        new_state, feedback, log = apply_action(
            simulation_id,
            payload.state,
            payload.action_id,
            payload.choice,
        )

        return {
            "state": new_state,
            "feedback": feedback,
            "log": log,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/score")
def score_simulation(payload: StateRequest):
    """
    Generate performance score.
    """
    score = generate_score(payload.state)
    return score


@router.post("/coach")
def coach_feedback(payload: StateRequest):
    """
    Generate coach summary feedback.
    """
    score = generate_score(payload.state)
    summary = generate_coach_summary(payload.state, score)

    return {
        "score": score,
        "summary": summary,
    }