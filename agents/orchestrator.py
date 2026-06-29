# agents/orchestrator.py
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm():
    return ChatGoogleGenerativeAI(
        model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
        google_api_key=os.getenv("LLM_API_KEY"),
        temperature=0.3,
    )

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

class OrchestratorState:
    def __init__(self):
        self.current_agent = None
        self.strategy_brief = None
        self.conversation_history = []
        self.hint_level = 0
        self.problem_solved = False

    def reset(self):
        self.__init__()

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

    def get_current_agent_name(self) -> str:
        role = self.state.current_agent
        if role:
            return AGENT_ROLES[role]["name"]
        return "None"

if __name__ == "__main__":
    orch = Orchestrator()
    print("=== Orchestrator Boot Test ===")
    print(f"Agents defined: {list(AGENT_ROLES.keys())}")
    print(f"Initial agent: {orch.state.current_agent}")

    route1 = orch.route("Find shortest path between nodes")
    print(f"Route (no brief yet): {route1} -> {AGENT_ROLES[route1]['name']}")

    orch.state.strategy_brief = {"pattern": "Dijkstra"}
    route2 = orch.route("Can you give me a hint?")
    print(f"Route (brief exists): {route2} -> {AGENT_ROLES[route2]['name']}")

    print("\n Orchestrator working correctly!")