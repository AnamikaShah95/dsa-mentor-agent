# agents/research_agent.py
"""
Day 6: Research Agent - real Gemini API integration
Combines the keyword pattern matcher with live LLM reasoning to produce
a validated StrategyBrief.
"""

import os
import json
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from knowledge.pattern_matcher import match_pattern, load_patterns
from agents.orchestrator import StrategyBrief

load_dotenv()

PROMPT_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "research_prompt.txt")


def load_system_prompt() -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


class ResearchAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
            google_api_key=os.getenv("LLM_API_KEY"),
            temperature=0.4,
        )
        self.system_prompt = load_system_prompt()
        self.patterns = load_patterns()

    def _extract_json(self, raw_text: str) -> dict:
        """Strips markdown code fences if Gemini adds them despite instructions."""
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE)
        return json.loads(cleaned)

    def analyze(self, problem_text: str) -> StrategyBrief:
        # Step 1: get a keyword-based suggestion first (cheap, fast, offline)
        suggested = match_pattern(problem_text, self.patterns)

        # Step 2: ask Gemini to confirm/refine using that suggestion as context
        user_message = (
            f"Student's problem:\n{problem_text}\n\n"
            f"Keyword-matcher suggestion: {suggested['name']} "
            f"(confidence score: {suggested.get('match_score', 0)})\n\n"
            f"Analyze the problem and respond with the JSON object as instructed."
        )

        response = self.llm.invoke([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_message)
        ])

        try:
            data = self._extract_json(response.content)
        except (json.JSONDecodeError, AttributeError) as e:
            # Fallback: if Gemini's output isn't valid JSON, use the keyword match alone
            print(f"[ResearchAgent] Warning: failed to parse Gemini JSON ({e}). Falling back to keyword match.")
            data = {
                "problem_title": problem_text[:40],
                "pattern": suggested["name"],
                "time_complexity": suggested["time_complexity"],
                "space_complexity": suggested["space_complexity"],
                "edge_cases": suggested["edge_cases"],
                "hints": suggested["hints"]
            }

        return StrategyBrief(
            problem_title=data.get("problem_title", problem_text[:40]),
            pattern=data.get("pattern", suggested["name"]),
            time_complexity=data.get("time_complexity", "O(n)"),
            space_complexity=data.get("space_complexity", "O(1)"),
            edge_cases=data.get("edge_cases", ["empty input"]),
            hints=data.get("hints", ["Think about the structure of the problem."]),
            language="python",
            difficulty="medium"
        )


# ── Live Test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 70)
    print("DAY 6: RESEARCH AGENT - LIVE GEMINI API TEST")
    print("=" * 70)

    agent = ResearchAgent()

    test_problem = (
        "A group of friends want to connect their houses with the cheapest "
        "possible set of internet cables so that everyone is connected, "
        "directly or indirectly."
    )

    print(f"\nProblem: {test_problem}\n")
    print("Calling Gemini 2.5 Flash...\n")

    brief = agent.analyze(test_problem)

    print("Generated StrategyBrief:")
    print(brief.to_json())
    print(f"\nValid: {brief.validate()}")
    print("\nLive API call completed successfully!")