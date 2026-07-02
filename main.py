# main.py
"""
DSA Mentor Agent — Main Entry Point
Launches the Streamlit app with side-by-side chat and code panels.
"""

import streamlit as st

st.set_page_config(
    page_title="DSA Mentor Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from ui.chat_panel import render_chat_panel
from ui.code_panel import render_code_panel

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .stChatMessage { border-radius: 12px; margin-bottom: 0.5rem; }
    .stTextArea textarea { font-family: 'Courier New', monospace; font-size: 13px; }
    div[data-testid="column"]:first-child { border-right: 1px solid #e0e0e0; padding-right: 1.5rem; }
    div[data-testid="column"]:last-child { padding-left: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
col_chat, col_code = st.columns([1, 1])

with col_chat:
    render_chat_panel()

with col_code:
    render_code_panel()