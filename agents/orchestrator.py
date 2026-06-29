# agents/orchestrator.py
import os
import json
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# ── LLM Setup ────────────────────────────────────────────────────────────────
def get_llm():
    return ChatGoogleGenerativeAI(
        model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
        google_api_key=os.getenv("LLM_API_KEY"),
        temperature=0.3,
    )

# ── Agent Role Definitions ────────────────────────────────────────────────────
AGENT_ROLES = {
    "research": {
        "name": "The Algorithmic Architect",
        "responsibility": (
            "Decompose untagged DSA problems into fundamental algorithm patterns. "
            "Extract structural patterns and generate a Strategy Brief JSON."
        ),
        "output": "strategy_brief"
    },
    "action": {
        "name": "The Polyglot Coach",
        "responsibility": (
            "Manage live Socratic dialogue with the student. "
            "Deliver progressive hints without leaking code solutions. "
            "Handle Python and Java code execution and validation."
        ),
        "output": "hint_or_feedback"
    }
}

# ── Data Contract: Strategy Brief ─────────────────────────────────────────────
@dataclass
class StrategyBrief:
    problem_title: str
    pattern: str
    time_complexity: str
    space_complexity: str
    edge_cases: List[str]
    hints: List[str]
    language: str = "python"
    difficulty: str = "medium"
    solved: bool = False

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2)

    @staticmethod
    def from_json(data: dict) -> "StrategyBrief":
        return StrategyBrief(**data)

    def get_next_hint(self, hint_level: int) -> Optional[str]:
        if hint_level < len(self.hints):
            return self.hints[hint_level]
        return None

    def validate(self) -> bool:
        required = [
            self.problem_title,
            self.pattern,
            self.time_complexity,
            self.space_complexity,
            self.edge_cases,
            self.hints
        ]
        return all(required) and len(self.hints) >= 2

# ── System State ──────────────────────────────────────────────────────────────
class OrchestratorState:
    def __init__(self):
        self.current_agent = None
        self.strategy_brief: Optional[StrategyBrief] = None
        self.conversation_history = []
        self.hint_level = 0
        self.problem_solved = False

    def reset(self):
        self.__init__()

# ── Handoff Logic ─────────────────────────────────────────────────────────────
class Orchestrator:
    def __init__(self):
        self.llm = get_llm()
        self.state = OrchestratorState()

    def route(self, user_input: str) -> str:
        if self.state.strategy_brief is None:
            self.state.current_agent = "research"
            return "research"
        else:
            self.state.current_agent = "action"
            return "action"

    def set_strategy_brief(self, brief: StrategyBrief):
        if not brief.validate():
            raise ValueError("StrategyBrief is missing required fields.")
        self.state.strategy_brief = brief

    def get_next_hint(self) -> Optional[str]:
        if self.state.strategy_brief:
            hint = self.state.strategy_brief.get_next_hint(self.state.hint_level)
            if hint:
                self.state.hint_level += 1
            return hint
        return None

    def get_current_agent_name(self) -> str:
        role = self.state.current_agent
        if role:
            return AGENT_ROLES[role]["name"]
        return "None"

# ── Test ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Day 2: StrategyBrief Contract Test ===\n")

    orch = Orchestrator()

    # Step 1: Route before brief exists
    route1 = orch.route("Find shortest path between nodes")
    print(f"Step 1 - Route (no brief): {route1} -> {AGENT_ROLES[route1]['name']}")

    # Step 2: Research Agent creates a StrategyBrief
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

    # Step 3: Validate and set brief
    orch.set_strategy_brief(brief)
    print(f"Step 2 - Brief valid: {brief.validate()}")
    print(f"Step 3 - Brief JSON:\n{brief.to_json()}")

    # Step 4: Route after brief exists
    route2 = orch.route("Give me a hint")
    print(f"\nStep 4 - Route (brief exists): {route2} -> {AGENT_ROLES[route2]['name']}")

    # Step 5: Progressive hint delivery
    print("\nStep 5 - Progressive Hints:")
    for i in range(4):
        hint = orch.get_next_hint()
        if hint:
            print(f"  Hint {i+1}: {hint}")
        else:
            print(f"  Hint {i+1}: No more hints available")

    print("\n✅ Day 2 Data Contract working correctly!")