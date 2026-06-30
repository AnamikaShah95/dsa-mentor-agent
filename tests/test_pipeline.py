# tests/test_pipeline.py
"""
Day 3: Mock Pipeline Evaluation
Simulates the full Research -> Action agent flow WITHOUT calling the real
Gemini API. Lets us verify orchestration logic, state handoffs, and the
Socratic hint flow before wiring in live LLM calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.orchestrator import Orchestrator, StrategyBrief, AGENT_ROLES


# ── Mock Research Agent ────────────────────────────────────────────────────
class MockResearchAgent:
    """
    Simulates the real research_agent.py without calling Gemini.
    In production this will send the problem to the LLM and parse
    a StrategyBrief JSON out of the response.
    """

    # A tiny fake "pattern database" to simulate keyword matching
    FAKE_PATTERNS = {
        "shortest path": "Dijkstra's Shortest Path",
        "connect": "Minimum Spanning Tree",
        "duplicate": "Hash Set / Two Pointers",
        "subsequence": "Dynamic Programming - LCS",
        "rotate": "Array Reversal / Two Pointers",
    }

    def analyze(self, problem_text: str) -> StrategyBrief:
        problem_lower = problem_text.lower()
        matched_pattern = "Brute Force (no pattern matched)"

        for keyword, pattern in self.FAKE_PATTERNS.items():
            if keyword in problem_lower:
                matched_pattern = pattern
                break

        # Simulate what the LLM would generate
        return StrategyBrief(
            problem_title=problem_text[:40],
            pattern=matched_pattern,
            time_complexity="O(E log V)" if "Dijkstra" in matched_pattern else "O(n)",
            space_complexity="O(V)" if "Dijkstra" in matched_pattern else "O(1)",
            edge_cases=["empty input", "single element", "all duplicates"],
            hints=[
                f"Think about what '{matched_pattern}' requires as a first step.",
                "What data structure would make repeated lookups faster?",
                "Trace through a small example by hand before coding."
            ],
            language="python",
            difficulty="medium"
        )


# ── Mock Action Agent ───────────────────────────────────────────────────────
class MockActionAgent:
    """
    Simulates the real action_agent.py Socratic dialogue without Gemini.
    In production this will use the StrategyBrief + conversation history
    to generate contextual Socratic responses via the LLM.
    """

    def respond(self, brief: StrategyBrief, hint_level: int, student_message: str) -> str:
        # Simulate code-leak filtering: if student asks for code directly, refuse
        leak_triggers = ["give me the code", "write the solution", "just solve it"]
        if any(trigger in student_message.lower() for trigger in leak_triggers):
            return (
                "I can't give you the full solution directly - let's work through "
                "it together. " + (brief.get_next_hint(hint_level) or "Try applying what we've discussed so far.")
            )

        hint = brief.get_next_hint(hint_level)
        if hint:
            return f"[Hint {hint_level + 1}] {hint}"
        return "You've used all available hints! Try implementing your approach now."


# ── Pipeline Simulation ──────────────────────────────────────────────────────
def run_mock_pipeline():
    print("=" * 60)
    print("DAY 3: MOCK PIPELINE EVALUATION")
    print("=" * 60)

    orch = Orchestrator()
    research_agent = MockResearchAgent()
    action_agent = MockActionAgent()

    # ── Step 1: Student submits a problem ──────────────────────────────────
    problem = "Find the shortest path between two nodes in a weighted graph"
    print(f"\n[Student submits problem]\n  '{problem}'")

    route = orch.route(problem)
    print(f"\n[Orchestrator routes to] {AGENT_ROLES[route]['name']} ({route})")

    # ── Step 2: Research Agent analyzes and produces StrategyBrief ─────────
    brief = research_agent.analyze(problem)
    orch.set_strategy_brief(brief)
    print(f"\n[Research Agent output]")
    print(f"  Pattern matched: {brief.pattern}")
    print(f"  Complexity target: {brief.time_complexity} time, {brief.space_complexity} space")
    print(f"  Edge cases flagged: {brief.edge_cases}")

    # ── Step 3: Orchestrator hands off to Action Agent ──────────────────────
    route2 = orch.route("ready to start")
    print(f"\n[Orchestrator routes to] {AGENT_ROLES[route2]['name']} ({route2})")

    # ── Step 4: Simulate a Socratic conversation ────────────────────────────
    student_messages = [
        "I don't know where to start",
        "Okay what data structure should I use?",
        "give me the code",          # tests the leak-filter
        "I think I understand now"
    ]

    print(f"\n[Simulated Socratic Dialogue]")
    for i, msg in enumerate(student_messages):
        response = action_agent.respond(brief, orch.state.hint_level, msg)
        print(f"\n  Student: {msg}")
        print(f"  Coach:   {response}")
        if not any(t in msg.lower() for t in ["give me the code", "write the solution", "just solve it"]):
            orch.state.hint_level += 1

    print("\n" + "=" * 60)
    print("PIPELINE RESULT")
    print("=" * 60)
    print(f"  Final agent: {orch.get_current_agent_name()}")
    print(f"  Hints delivered: {orch.state.hint_level}")
    print(f"  Code leak attempts blocked: 1")
    print(f"  StrategyBrief intact: {orch.state.strategy_brief.validate()}")
    print("\nMock pipeline completed successfully - no live API calls made.")


if __name__ == "__main__":
    run_mock_pipeline()