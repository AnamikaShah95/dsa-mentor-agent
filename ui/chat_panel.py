# ui/chat_panel.py
"""
Day 10: Chat Panel UI
Left panel of the Streamlit interface.
Handles problem input, conversation display, and hint progression.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agents.orchestrator import Orchestrator, StrategyBrief
from agents.research_agent import ResearchAgent
from agents.action_agent import ActionAgent


def initialize_session():
    """Initialize all session state variables on first load."""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = Orchestrator()
    if "research_agent" not in st.session_state:
        st.session_state.research_agent = ResearchAgent()
    if "action_agent" not in st.session_state:
        st.session_state.action_agent = ActionAgent()
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "hint_level" not in st.session_state:
        st.session_state.hint_level = 0
    if "brief" not in st.session_state:
        st.session_state.brief = None
    if "problem_submitted" not in st.session_state:
        st.session_state.problem_submitted = False
    if "language" not in st.session_state:
        st.session_state.language = "python"


def render_chat_panel():
    initialize_session()

    st.markdown("### 🧠 DSA Mentor")
    st.caption("Powered by Gemini 2.5 Flash · Socratic Method")
    st.divider()

    # ── Problem Input Area ────────────────────────────────────────────────
    if not st.session_state.problem_submitted:
        st.markdown("**Submit your DSA problem to get started:**")

        problem = st.text_area(
            label="Problem Description",
            placeholder=(
                "Describe your problem in plain English...\n\n"
                "e.g. 'Find the shortest path between two cities in a weighted road network.'"
            ),
            height=140,
            key="problem_input"
        )

        col1, col2 = st.columns([2, 1])
        with col1:
            language = st.selectbox(
                "Language", ["python", "java"], key="lang_select"
            )
        with col2:
            st.write("")
            st.write("")
            submit = st.button("🚀 Analyze Problem", use_container_width=True)

        if submit and problem.strip():
            with st.spinner("The Algorithmic Architect is analyzing your problem..."):
                try:
                    brief = st.session_state.research_agent.analyze(problem)
                    st.session_state.orchestrator.set_strategy_brief(brief)
                    st.session_state.brief = brief
                    st.session_state.language = language
                    st.session_state.problem_submitted = True

                    # First coach message
                    opening = (
                        f"Great! I've analyzed your problem. "
                        f"Before we dive in — can you tell me in your own words "
                        f"what the inputs and outputs of this problem are?"
                    )
                    st.session_state.conversation.append({
                        "role": "coach",
                        "content": opening
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")

        elif submit and not problem.strip():
            st.warning("Please describe your problem first.")

    # ── Conversation Display ──────────────────────────────────────────────
    else:
        brief = st.session_state.brief

        # Show brief summary at top
        with st.expander("📋 Problem Analysis", expanded=False):
            st.markdown(f"**Pattern:** {brief.pattern}")
            st.markdown(f"**Complexity:** {brief.time_complexity} time · {brief.space_complexity} space")
            st.markdown(f"**Difficulty:** {brief.difficulty.capitalize()}")
            st.markdown(f"**Hints available:** {len(brief.hints)}")

        st.divider()

        # Render conversation history
        for turn in st.session_state.conversation:
            if turn["role"] == "coach":
                with st.chat_message("assistant", avatar="🧠"):
                    st.markdown(turn["content"])
            else:
                with st.chat_message("user", avatar="👩‍💻"):
                    st.markdown(turn["content"])

        # Student input
        student_msg = st.chat_input("Type your response or question...")

        if student_msg:
            st.session_state.conversation.append({
                "role": "student",
                "content": student_msg
            })

            with st.spinner("Coach is thinking..."):
                result = st.session_state.action_agent.respond(
                    brief=st.session_state.brief,
                    conversation_history=st.session_state.conversation[:-1],
                    student_message=student_msg,
                    hint_level=st.session_state.hint_level
                )

            st.session_state.hint_level = result["hint_level"]
            st.session_state.conversation.append({
                "role": "coach",
                "content": result["reply"]
            })

            if result["bypass_detected"]:
                st.toast("⚠️ Bypass attempt detected and redirected.", icon="🛡️")
            if result["leak_detected"]:
                st.toast("🔒 Code leak filtered from response.", icon="🔒")

            st.rerun()

        # Reset button
        st.divider()
        if st.button("🔄 Start New Problem", use_container_width=True):
            for key in ["orchestrator", "research_agent", "action_agent",
                        "conversation", "hint_level", "brief",
                        "problem_submitted", "language"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()