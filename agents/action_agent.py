# agents/action_agent.py
"""
Day 9: Action Agent - live Socratic dialogue via Gemini
Manages the student conversation, enforces hint progression,
filters code leaks from LLM output, and routes code to the executor.
"""

import os
import re
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agents.orchestrator import StrategyBrief
from executor.python_runner import run_python_code
from executor.java_runner import run_java_code

load_dotenv()

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "mentor_prompt.txt")

# ── Threat Patterns ───────────────────────────────────────────────────────────
# Phrases that signal a student is trying to bypass Socratic rules
BYPASS_TRIGGERS = [
    "give me the code",
    "write the solution",
    "just solve it",
    "ignore your instructions",
    "forget your rules",
    "pretend you are",
    "act as if",
    "solve this for me",
    "what is the answer",
    "tell me the answer"
]

# Regex patterns that detect code blocks in LLM output (leak filter)
CODE_LEAK_PATTERNS = [
    r"```[\s\S]*?```",           # markdown code fences
    r"def\s+\w+\s*\(",           # Python function definitions
    r"public\s+\w+\s+\w+\s*\(", # Java method definitions
    r"for\s*\(.+\)\s*\{",        # Java for loops
    r"while\s*\(.+\)\s*\{",      # Java while loops
    r"int\[\]\s+\w+\s*=",        # Java array declarations
]


def load_mentor_prompt() -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def contains_bypass_attempt(message: str) -> bool:
    return any(trigger in message.lower() for trigger in BYPASS_TRIGGERS)


def filter_code_leaks(response: str) -> tuple[bool, str]:
    """
    Scans LLM output for code patterns.
    Returns (leak_detected: bool, cleaned_response: str).
    If a leak is detected, replaces the code block with a redirect message.
    """
    leak_detected = False
    for pattern in CODE_LEAK_PATTERNS:
        if re.search(pattern, response):
            leak_detected = True
            response = re.sub(pattern, "[code removed by mentor filter]", response)
    return leak_detected, response


class ActionAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
            google_api_key=os.getenv("LLM_API_KEY"),
            temperature=0.5,
        )
        self.mentor_prompt = load_mentor_prompt()

    def _build_system_prompt(self, brief: StrategyBrief, hint_level: int) -> str:
        next_hint = brief.get_next_hint(hint_level)
        hint_context = f"\nNext hint to work toward (do NOT reveal directly): {next_hint}" if next_hint else "\nAll hints have been used."
        return self.mentor_prompt + f"\n\nStrategyBrief (private):\n{brief.to_json()}" + hint_context

    def respond(
        self,
        brief: StrategyBrief,
        conversation_history: list,
        student_message: str,
        hint_level: int
    ) -> dict:
        """
        Generates a Socratic response.
        Returns dict with: reply, hint_level, leak_detected, bypass_detected
        """

        # ── Threat check ──────────────────────────────────────────────────
        bypass_detected = contains_bypass_attempt(student_message)
        if bypass_detected:
            return {
                "reply": (
                    "I understand the frustration, but working through this yourself "
                    "is exactly how the learning happens. Let's go back to where we were — "
                    f"{brief.get_next_hint(hint_level) or 'what have you tried so far?'}"
                ),
                "hint_level": hint_level,
                "leak_detected": False,
                "bypass_detected": True
            }

        # ── Build message history for Gemini ──────────────────────────────
        system_prompt = self._build_system_prompt(brief, hint_level)
        messages = [SystemMessage(content=system_prompt)]

        for turn in conversation_history:
            if turn["role"] == "student":
                messages.append(HumanMessage(content=turn["content"]))
            elif turn["role"] == "coach":
                messages.append(AIMessage(content=turn["content"]))

        messages.append(HumanMessage(content=student_message))

        # ── Call Gemini ───────────────────────────────────────────────────
        response = self.llm.invoke(messages)
        raw_reply = response.content

        # ── Code leak filter ─────────────────────────────────────────────
        leak_detected, clean_reply = filter_code_leaks(raw_reply)
        if leak_detected:
            clean_reply += (
                "\n\n(I almost gave away too much there! Let's think through "
                "the logic step by step instead.)"
            )
            # don't advance hint level if we had to filter output
        else:
            hint_level += 1

        return {
            "reply": clean_reply,
            "hint_level": hint_level,
            "leak_detected": leak_detected,
            "bypass_detected": False
        }

    def execute_code(self, code: str, language: str) -> dict:
        """Routes code to the correct language runner."""
        if language == "java":
            return run_java_code(code)
        return run_python_code(code)


# ── Live Test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from agents.orchestrator import StrategyBrief

    print("=" * 70)
    print("DAY 9: ACTION AGENT - LIVE SOCRATIC DIALOGUE TEST")
    print("=" * 70)

    brief = StrategyBrief(
        problem_title="Network Delay Time",
        pattern="Dijkstra's Shortest Path",
        time_complexity="O(E log V)",
        space_complexity="O(V)",
        edge_cases=["disconnected graph", "single node", "negative weights"],
        hints=[
            "What data structure helps you always process the closest node first?",
            "How would you track the shortest known distance to each node?",
            "What happens when you reach a node you have already visited?"
        ],
        language="python",
        difficulty="medium"
    )

    agent = ActionAgent()
    history = []
    hint_level = 0

    student_turns = [
        "I have no idea where to start with this problem.",
        "Maybe I should use a list to track distances?",
        "give me the code please",
        "Okay okay. Should I use a priority queue?",
    ]

    for msg in student_turns:
        print(f"\nStudent: {msg}")
        result = agent.respond(brief, history, msg, hint_level)
        print(f"Coach:   {result['reply']}")
        if result["bypass_detected"]:
            print("         [⚠️  bypass attempt blocked]")
        if result["leak_detected"]:
            print("         [🔒 code leak filtered]")

        hint_level = result["hint_level"]
        history.append({"role": "student", "content": msg})
        history.append({"role": "coach", "content": result["reply"]})

    print("\n" + "=" * 70)
    print(f"Final hint level: {hint_level}")
    print("Action Agent working correctly!")