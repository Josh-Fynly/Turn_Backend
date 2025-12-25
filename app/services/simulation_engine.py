import json
from pathlib import Path
from typing import Dict, Any, Tuple


BASE_PATH = Path(__file__).parent.parent / "data" / "scenarios"


def load_scenario(industry: str, role: str) -> Dict[str, Any]:
    """
    Load a scenario using industry and role naming.
    """
    filename = f"{industry}_{role}.json"
    path = BASE_PATH / filename

    if not path.exists():
        raise ValueError("Scenario not found")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_simulation(simulation_id: str) -> Dict[str, Any]:
    """
    Load a simulation by its unique ID.
    """
    file_path = BASE_PATH / f"{simulation_id}.json"

    if not file_path.exists():
        raise ValueError("Simulation scenario not found")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def initialize_state(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize a fresh simulation state.
    """
    return scenario["initial_state"].copy()


def apply_action(
    scenario: Dict[str, Any],
    state: Dict[str, Any],
    action_id: str,
    choice: str,
) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    """
    Apply a decision to the current simulation state.
    """
    new_state = state.copy()

    if action_id not in scenario["actions"]:
        raise ValueError("Invalid action")

    action = scenario["actions"][action_id]

    if choice not in action["choices"]:
        raise ValueError("Invalid choice")

    outcome = action["choices"][choice]

    for key, delta in outcome.get("effects", {}).items():
        new_state[key] = round(new_state.get(key, 0) + delta, 2)

    feedback = outcome.get("feedback", "")

    log = {
        "action_id": action_id,
        "choice": choice,
        "effects": outcome.get("effects", {}),
    }

    return new_state, feedback, log


def generate_score(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a simple performance score from the current state.
    """
    score = {
        "execution": max(0, min(1, 1 - abs(state.get("deadline_days", 0)) / 10)),
        "risk_management": max(0, 1 - state.get("risk", 0)),
        "stakeholder_management": state.get("stakeholder_trust", 0),
    }

    score["overall"] = round(sum(score.values()) / len(score), 2)
    return score


def generate_coach_summary(state: Dict[str, Any], score: Dict[str, Any]) -> str:
    """
    Generate qualitative coaching feedback.
    """
    risk = state.get("risk", 0)
    trust = state.get("stakeholder_trust", 0)
    deadline = state.get("deadline_days", 0)
    overall = score.get("overall", 0)

    insights = []

    if risk > 0.6:
        insights.append(
            "Your decisions significantly increased delivery risk, which often leads to downstream issues."
        )
    elif risk < 0.3:
        insights.append(
            "You proactively reduced risk, showing strong judgment under pressure."
        )

    if trust < 0.4:
        insights.append(
            "Stakeholder trust declined, which may affect future alignment."
        )
    elif trust > 0.7:
        insights.append(
            "You strengthened stakeholder confidence during uncertainty."
        )

    if deadline < 0:
        insights.append(
            "You traded speed for quality — a reasonable call in regulated environments."
        )
    elif deadline > 10:
        insights.append(
            "You preserved schedule flexibility, giving your team room to adapt."
        )

    return (
        f"Overall performance score: {overall}. "
        + " ".join(insights)
        + " Focus on balancing speed, trust, and risk as complexity increases."
    )