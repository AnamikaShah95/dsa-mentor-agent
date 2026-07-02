import streamlit as st

st.set_page_config(
    page_title="DSA Mentor Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from ui.chat_panel import render_chat_panel
from ui.code_panel import render_code_panel

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 0.5rem 0 1rem 0;">
    <h2 style="margin:0; color:#1f2937;">🧠 DSA Mentor Agent</h2>
    <p style="margin:0; color:#6b7280; font-size:14px;">
        Autonomous Dual-Agent AI Tutoring · Socratic Method · Gemini 2.5 Flash
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Layout ────────────────────────────────────────────────────────────────────
col_chat, col_code = st.columns([1, 1])

with col_chat:
    render_chat_panel()

with col_code:
    render_code_panel()