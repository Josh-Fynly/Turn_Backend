import json
from pathlib import Path
from typing import Dict, Any, Tuple


BASE_PATH = Path(__file__).parent.parent / "data" / "scenarios"
SIMULATION_PATH = Path(__file__).parent.parent / "data" / "scenarios"


def load_scenario(industry: str, role: str) -> Dict[str, Any]:
    filename = f"{industry}_{role}.json"
    path = BASE_PATH / filename

    if not path.exists():
        raise ValueError("Scenario not found")

    with open(path, "r") as f:
        scenario = json.load(f)

    return scenario


def load_simulation(simulation_id: str) -> Dict[str, Any]:
    """
    Load a simulation by unique simulation ID.
    Used for demo, API exposure, and future expansion.
    """
    file_path = SIMULATION_PATH / f"{simulation_id}.json"

    if not file_path.exists():
        raise ValueError("Simulation scenario not found")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_action(
    state: Dict[str, Any],
    action_id: str,
    choice: str,
) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    new_state = state.copy()

    # Existing demo logic preserved
    scenario = load_scenario("financial", "product_manager")
    action = scenario["actions"][action_id]
    outcome = action["choices"][choice]

    for key, delta in outcome["effects"].items():
        new_state[key] = round(new_state.get(key, 0) + delta, 2)

    feedback = outcome["feedback"]

    return new_state, feedback, {
        "action_id": action_id,
        "choice": choice,
        "effects": outcome["effects"],
    }


def generate_score(state: Dict[str, Any]) -> Dict[str, Any]:
    score = {
        "execution": max(0, min(1, 1 - abs(state["deadline_days"]) / 10)),
        "risk_management": max(0, 1 - state["risk"]),
        "stakeholder_management": state["stakeholder_trust"],
    }
    score["overall"] = round(sum(score.values()) / len(score), 2)
    return score


def generate_coach_summary(state: Dict[str, Any], score: Dict[str, Any]) -> str:
    return (
        f"Overall score: {score['overall']}. "
        f"You balanced delivery speed with stakeholder trust. "
        f"To improve, focus on reducing risk earlier while maintaining momentum."
    )