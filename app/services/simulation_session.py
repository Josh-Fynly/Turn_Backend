from typing import Dict, Any
import uuid

# In-memory demo store (RESET ON RESTART)
_SIMULATIONS: Dict[str, Dict[str, Any]] = {}

def create_simulation(initial_state: Dict[str, Any], meta: Dict[str, Any]) -> str:
    simulation_id = f"sim_{uuid.uuid4().hex[:8]}"
    _SIMULATIONS[simulation_id] = {
        "state": initial_state,
        "meta": meta,
        "history": []
    }
    return simulation_id

def get_simulation(simulation_id: str) -> Dict[str, Any]:
    if simulation_id not in _SIMULATIONS:
        raise KeyError("Simulation not found")
    return _SIMULATIONS[simulation_id]

def update_simulation(simulation_id: str, state: Dict[str, Any], action_log: Dict[str, Any]):
    sim = get_simulation(simulation_id)
    sim["state"] = state
    sim["history"].append(action_log)
