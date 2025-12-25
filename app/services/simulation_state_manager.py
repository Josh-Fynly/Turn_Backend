# app/services/simulation_state_manager.py

import uuid
from typing import Dict, Any, Tuple

from app.services.simulation_engine import (
    load_simulation,
    apply_action,
    generate_score,
    generate_coach_summary,
)

# In-memory store (demo-safe)
_SIMULATION_SESSIONS: Dict[str, Dict[str, Any]] = {}


class SimulationStateManager:
    """
    Manages in-memory simulation sessions.
    One session = one user simulation run.
    """

    def start_simulation(self, simulation_id: str) -> Tuple[str, Dict[str, Any]]:
        simulation = load_simulation(simulation_id)

        session_id = str(uuid.uuid4())

        _SIMULATION_SESSIONS[session_id] = {
            "simulation_id": simulation_id,
            "simulation": simulation,
            "state": simulation["initial_state"].copy(),
            "history": [],
            "current_step": None,
            "completed": False,
        }

        return session_id, _SIMULATION_SESSIONS[session_id]

    def get_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in _SIMULATION_SESSIONS:
            raise ValueError("Simulation session not found")
        return _SIMULATION_SESSIONS[session_id]

    def apply_action(
        self, session_id: str, action_id: str, choice: str
    ) -> Tuple[Dict[str, Any], str]:
        session = self.get_session(session_id)

        if session["completed"]:
            raise ValueError("Simulation already completed")

        current_state = session["state"]

        new_state, feedback, meta = apply_action(
            current_state, action_id, choice
        )

        session["state"] = new_state
        session["current_step"] = action_id
        session["history"].append(
            {
                "action_id": action_id,
                "choice": choice,
                "effects": meta["effects"],
            }
        )

        return new_state, feedback

    def complete_simulation(self, session_id: str) -> Dict[str, Any]:
        session = self.get_session(session_id)

        if session["completed"]:
            raise ValueError("Simulation already completed")

        score = generate_score(session["state"])
        summary = generate_coach_summary(session["state"], score)

        session["completed"] = True
        session["final_score"] = score
        session["coach_summary"] = summary

        return {
            "score": score,
            "coach_summary": summary,
            "history": session["history"],
        }


# Singleton instance (important)
simulation_state_manager = SimulationStateManager()
