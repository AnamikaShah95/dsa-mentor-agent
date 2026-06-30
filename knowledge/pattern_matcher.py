# knowledge/pattern_matcher.py
"""
Day 4: Pattern Matching Engine
Loads patterns.json and matches a free-text problem description to the
best-fitting algorithmic pattern using keyword overlap scoring.
"""

import json
import os

PATTERNS_PATH = os.path.join(os.path.dirname(__file__), "patterns.json")


def load_patterns() -> list:
    with open(PATTERNS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["patterns"]


def match_pattern(problem_text: str, patterns: list = None) -> dict:
    """
    Scores each pattern by counting how many of its keywords appear
    in the problem text. Returns the highest scoring pattern, or a
    fallback 'no match' pattern if nothing scores above zero.
    """
    if patterns is None:
        patterns = load_patterns()

    text = problem_text.lower()
    best_match = None
    best_score = 0

    for pattern in patterns:
        score = sum(1 for kw in pattern["keywords"] if kw in text)
        if score > best_score:
            best_score = score
            best_match = pattern

    if best_match is None:
        return {
            "id": "unmatched",
            "name": "Brute Force (no pattern matched)",
            "category": "Unknown",
            "keywords": [],
            "time_complexity": "O(n) - O(n^2) depending on approach",
            "space_complexity": "O(1) - O(n)",
            "edge_cases": ["empty input", "single element"],
            "hints": [
                "What's the most direct way to check every possibility?",
                "Could you reduce repeated work with a data structure?",
                "Is there a known pattern this resembles once simplified?"
            ]
        }

    return {**best_match, "match_score": best_score}


def get_top_matches(problem_text: str, top_n: int = 3, patterns: list = None) -> list:
    """Returns the top N candidate patterns, useful for ambiguous problems."""
    if patterns is None:
        patterns = load_patterns()

    text = problem_text.lower()
    scored = []
    for pattern in patterns:
        score = sum(1 for kw in pattern["keywords"] if kw in text)
        if score > 0:
            scored.append({**pattern, "match_score": score})

    scored.sort(key=lambda p: p["match_score"], reverse=True)
    return scored[:top_n]


# ── Test ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_problems = [
        "Find the shortest path between two nodes in a weighted graph",
        "Connecting cities with minimal cost using cables",
        "Find the longest substring without repeating characters",
        "Detect if a linked list has a cycle",
        "Given a knapsack capacity, maximize the total value of items",
        "What is the best way to schedule overlapping meetings",
        "Solve this completely unrelated nonsense problem about cats"
    ]

    patterns = load_patterns()
    print(f"Loaded {len(patterns)} patterns from knowledge base.\n")
    print("=" * 70)

    for problem in test_problems:
        match = match_pattern(problem, patterns)
        print(f"\nProblem: {problem}")
        print(f"  -> Matched pattern: {match['name']}")
        print(f"  -> Category: {match['category']}")
        print(f"  -> Score: {match.get('match_score', 0)}")

    print("\n" + "=" * 70)
    print("Top 3 candidates for an ambiguous query:")
    ambiguous = "Find the minimum number of meetings to schedule using a greedy interval approach"
    top = get_top_matches(ambiguous, top_n=3, patterns=patterns)
    for p in top:
        print(f"  - {p['name']} (score: {p['match_score']})")

    print("\nPattern matcher working correctly!")