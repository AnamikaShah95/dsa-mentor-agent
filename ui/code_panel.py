# ui/code_panel.py
"""
Day 11: Code Panel UI (polished)
Adds execution-to-chat feedback loop so the coach can comment on
the student's code output directly in the conversation.
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
    st.caption("Write, run, and get coach feedback on your solution")
    st.divider()

    language = st.session_state.get("language", "python")
    starter = PYTHON_STARTER if language == "python" else JAVA_STARTER
    lang_label = "Python 🐍" if language == "python" else "Java ☕"

    st.markdown(f"**Language:** {lang_label}")

    code = st.text_area(
        label="Your Code",
        value=st.session_state.get("current_code", starter),
        height=300,
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

    with st.expander("📥 Provide Input (stdin)", expanded=False):
        stdin_val = st.text_area(
            "Input values",
            height=80,
            key="stdin_input",
            label_visibility="collapsed"
        )

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
                st.error("⏱️ Time Limit Exceeded — check for infinite loops.")
                output_summary = "My code timed out after 5 seconds."

            elif result.get("compile_error"):
                st.error("🔴 Compilation Error")
                st.code(result["stderr"], language="text")
                output_summary = f"My code has a compilation error:\n{result['stderr'][:300]}"

            elif result["success"]:
                st.success("✅ Ran successfully")
                if result["stdout"]:
                    st.code(result["stdout"], language="text")
                else:
                    st.info("No output produced.")
                output_summary = f"My code ran successfully. Output:\n{result['stdout'][:300]}"

            else:
                st.error("🔴 Runtime Error")
                if result["stdout"]:
                    st.code(result["stdout"], language="text")
                st.code(result["stderr"], language="text")
                output_summary = f"My code has a runtime error:\n{result['stderr'][:300]}"

            # ── Send to coach if problem is active ────────────────────────
            if st.session_state.get("problem_submitted") and st.session_state.get("brief"):
                st.divider()
                if st.button("💬 Ask Coach to Review My Output", use_container_width=True):
                    coach_message = (
                        f"I ran my {language} code and here's what happened:\n\n"
                        f"```\n{code[:500]}\n```\n\n"
                        f"Result: {output_summary}"
                    )
                    st.session_state.conversation.append({
                        "role": "student",
                        "content": coach_message
                    })

                    with st.spinner("Coach is reviewing your code..."):
                        result_coach = st.session_state.action_agent.respond(
                            brief=st.session_state.brief,
                            conversation_history=st.session_state.conversation[:-1],
                            student_message=coach_message,
                            hint_level=st.session_state.hint_level
                        )

                    st.session_state.hint_level = result_coach["hint_level"]
                    st.session_state.conversation.append({
                        "role": "coach",
                        "content": result_coach["reply"]
                    })
                    st.rerun()