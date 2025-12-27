import streamlit as st
from app.services.simulation_engine import (
    load_simulation,
    apply_action,
    generate_score,
    generate_coach_summary,
)

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Turnve — Career Simulation Demo",
    layout="centered",
)

st.title("Turnve Career Simulation")
st.caption("Experience real work — not courses.")

# -----------------------------
# Session State Initialization
# -----------------------------
if "simulation_id" not in st.session_state:
    st.session_state.simulation_id = "technology_product_associate"

if "scenario" not in st.session_state:
    st.session_state.scenario = load_simulation(
        st.session_state.simulation_id
    )

if "state" not in st.session_state:
    st.session_state.state = (
        st.session_state.scenario["initial_state"].copy()
    )

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# Project Brief
# -----------------------------
with st.container():
    st.subheader("📌 Project Brief")

    meta = st.session_state.scenario.get("meta", {})
    context = st.session_state.scenario.get("context", {})

    st.markdown(f"**Role:** {meta.get('role')}")
    st.markdown(f"**Industry:** {meta.get('industry')}")
    st.markdown("---")
    st.write(context.get("summary", ""))

# -----------------------------
# Current State Display
# -----------------------------
with st.container():
    st.subheader("📊 Current Project State")
    st.json(st.session_state.state)

# -----------------------------
# Decision Interface
# -----------------------------
st.subheader("🧠 Make a Decision")

actions = st.session_state.scenario.get("actions", {})

action_id = st.selectbox(
    "Select a situation",
    options=list(actions.keys()),
)

choices = actions[action_id]["choices"]

choice_id = st.radio(
    "How do you respond?",
    options=list(choices.keys()),
    format_func=lambda c: choices[c].get("label", c),
)

if st.button("Submit Decision"):
    new_state, feedback, log = apply_action(
        simulation_id=st.session_state.simulation_id,
        state=st.session_state.state,
        action_id=action_id,
        choice=choice_id,
    )

    st.session_state.state = new_state
    st.session_state.history.append(
        {
            "action": action_id,
            "choice": choice_id,
            "feedback": feedback,
        }
    )

    st.success("Decision applied.")
    st.info(feedback)

# -----------------------------
# History
# -----------------------------
if st.session_state.history:
    st.subheader("🗂 Decision History")
    for h in st.session_state.history:
        st.write(
            f"**{h['action']} → {h['choice']}**\n\n{h['feedback']}"
        )

# -----------------------------
# Score & Coach Feedback
# -----------------------------
if st.button("Finish Simulation"):
    score = generate_score(st.session_state.state)
    summary = generate_coach_summary(
        st.session_state.state, score
    )

    st.subheader("🏁 Simulation Results")
    st.json(score)
    st.markdown("### AI Coach Feedback")
    st.write(summary)