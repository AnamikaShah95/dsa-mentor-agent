# ui/code_panel.py
"""
Day 10: Code Panel UI
Right panel of the Streamlit interface.
Code editor, execution button, and output console.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from executor.python_runner import run_python_code
from executor.java_runner import run_java_code


PYTHON_STARTER = '''# Write your solution here
def solution():
    pass

# Test your solution
print(solution())
'''

JAVA_STARTER = '''public class Solution {
    public static void main(String[] args) {
        // Write your solution here
        System.out.println("Hello!");
    }
}
'''


def render_code_panel():
    st.markdown("### 💻 Code Editor")
    st.caption("Write and run your solution here")
    st.divider()

    language = st.session_state.get("language", "python")
    starter = PYTHON_STARTER if language == "python" else JAVA_STARTER
    lang_label = "Python 🐍" if language == "python" else "Java ☕"

    st.markdown(f"**Language:** {lang_label}")

    # Code editor
    code = st.text_area(
        label="Your Code",
        value=st.session_state.get("current_code", starter),
        height=320,
        key="code_editor",
        label_visibility="collapsed"
    )

    st.session_state.current_code = code

    col1, col2 = st.columns([1, 1])
    with col1:
        run_btn = st.button("▶️ Run Code", use_container_width=True, type="primary")
    with col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)

    if clear_btn:
        st.session_state.current_code = starter
        st.rerun()

    # Stdin input
    with st.expander("📥 Provide Input (stdin)", expanded=False):
        stdin_val = st.text_area(
            "Input values (one per line)",
            height=80,
            key="stdin_input",
            label_visibility="collapsed"
        )

    # Execute
    if run_btn:
        if not code.strip():
            st.warning("Write some code first!")
        else:
            with st.spinner("Running your code..."):
                if language == "java":
                    result = run_java_code(code, stdin_input=stdin_val or "")
                else:
                    result = run_python_code(code, stdin_input=stdin_val or "")

            st.divider()
            st.markdown("**📤 Output Console**")

            if result["timed_out"]:
                st.error("⏱️ Time Limit Exceeded — your code ran for more than 5 seconds. Check for infinite loops.")
            elif result.get("compile_error"):
                st.error("🔴 Compilation Error")
                st.code(result["stderr"], language="text")
            elif result["success"]:
                st.success("✅ Ran successfully")
                if result["stdout"]:
                    st.code(result["stdout"], language="text")
                else:
                    st.info("No output produced.")
            else:
                st.error("🔴 Runtime Error")
                if result["stdout"]:
                    st.code(result["stdout"], language="text")
                st.code(result["stderr"], language="text")