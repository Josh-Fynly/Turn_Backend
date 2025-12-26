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

router = APIRouter(
    prefix="/demo/simulations",
    tags=["Demo Simulations"],
)


class ActionRequest(BaseModel):
    state: Dict[str, Any]
    action_id: str
    choice: str


@router.get("/{simulation_id}")
def get_demo_simulation(simulation_id: str):
    try:
        scenario = load_simulation(simulation_id)
        initial_state = initialize_state(scenario)

        return {
            "simulation_id": simulation_id,
            "meta": scenario.get("meta", {}),
            "initial_state": initial_state,
            "actions": scenario.get("actions", {}),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{simulation_id}/action")
def run_demo_action(simulation_id: str, payload: ActionRequest):
    try:
        new_state, feedback, log = apply_action(
            simulation_id=simulation_id,
            state=payload.state,
            action_id=payload.action_id,
            choice=payload.choice,
        )

        score = generate_score(new_state)
        coach_summary = generate_coach_summary(new_state, score)

        return {
            "new_state": new_state,
            "feedback": feedback,
            "score": score,
            "coach_summary": coach_summary,
            "log": log,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
def demo_health_check():
    return {"status": "ok", "demo": "simulation"}