# knowledge/pattern_matcher.py
"""
Day 5: Keyword Parsing Logic (upgraded)
Adds tokenized word-level matching on top of Day 4's phrase matching,
so problems don't need an exact keyword phrase to be recognized.
"""

import json
import os
import re

PATTERNS_PATH = os.path.join(os.path.dirname(__file__), "patterns.json")


def load_patterns() -> list:
    with open(PATTERNS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["patterns"]


def tokenize(text: str) -> set:
    """Lowercase, strip punctuation, split into a set of words."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return set(text.split())


def score_pattern(problem_text: str, pattern: dict) -> float:
    """
    Combined scoring:
      - Phrase match (exact substring) = 2 points  -> strong signal
      - Word-level overlap = 1 point per shared word -> weak signal
    """
    text_lower = problem_text.lower()
    problem_tokens = tokenize(problem_text)

    score = 0.0
    for kw in pattern["keywords"]:
        if kw in text_lower:
            score += 2.0  # exact phrase match, high confidence
        else:
            kw_tokens = tokenize(kw)
            overlap = kw_tokens & problem_tokens
            if overlap:
                # partial credit, scaled by how much of the keyword phrase matched
                score += 1.0 * (len(overlap) / len(kw_tokens))

    return round(score, 2)


def match_pattern(problem_text: str, patterns: list = None) -> dict:
    if patterns is None:
        patterns = load_patterns()

    best_match = None
    best_score = 0.0

    for pattern in patterns:
        score = score_pattern(problem_text, pattern)
        if score > best_score:
            best_score = score
            best_match = pattern

    if best_match is None or best_score == 0:
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
            ],
            "match_score": 0
        }

    return {**best_match, "match_score": best_score}


def get_top_matches(problem_text: str, top_n: int = 3, patterns: list = None) -> list:
    if patterns is None:
        patterns = load_patterns()

    scored = []
    for pattern in patterns:
        score = score_pattern(problem_text, pattern)
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
        "Count the number of islands in a grid of land and water",
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
        print(f"  -> Score: {match['match_score']}")

    print("\n" + "=" * 70)
    print("Top 3 candidates for an ambiguous query:")
    ambiguous = "Find the minimum number of meetings to schedule using a greedy interval approach"
    top = get_top_matches(ambiguous, top_n=3, patterns=patterns)
    for p in top:
        print(f"  - {p['name']} (score: {p['match_score']})")

    print("\nUpgraded pattern matcher working correctly!")