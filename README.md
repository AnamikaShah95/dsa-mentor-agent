# 🧠 DSA Mentor Agent
### Autonomous Dual-Agent AI Tutoring System

> *"Don't give students the answer — give them the question that leads there."*

A multi-agent AI system that guides students through Data Structures & Algorithms using the **Socratic Method**. Built with LangChain, Gemini 2.5 Flash, and Streamlit — two specialized agents collaborate to decompose problems and deliver progressive hints without ever leaking code solutions.

---

## ⚡ Key Stats

| Metric | Value |
|--------|-------|
| DSA Paradigms Covered | 40+ |
| Supported Languages | Python, Java |
| Execution Timeout | 5 seconds |
| Validation Test Cases | 10 per problem |
| Direct Code Leaks | 0 |
| MVP Build Time | 13 days |

---

## 🤖 Dual-Agent Architecture

### Agent 1 — The Algorithmic Architect *(Research Agent)*
- Decomposes untagged, story-based problems into fundamental algorithm patterns
- Extracts structural signals: `"connecting cities with minimal cost"` → `Minimum Spanning Tree`
- Produces a structured **StrategyBrief JSON** containing:
  - Target time/space complexity
  - Edge case conditions
  - A progressive hint sequence (never exposed all at once)

### Agent 2 — The Polyglot Coach *(Action Agent)*
- Manages live Socratic dialogue with the student
- Enforces hint progression — one hint at a time, based on student responses
- Runs student code in an isolated sandbox (Python subprocess / Java JVM)
- Never outputs working solution code until the student solves it themselves

### Orchestrator
- Routes input to the correct agent based on system state
- Manages the `StrategyBrief` handoff between agents
- Tracks hint level, conversation history, and problem-solved state

---

## 🗂️ Project Structure

```
DSA_Coding Mentor Agent/
├── main.py                    # Streamlit app entry point
├── requirements.txt
├── .env                       # API keys (never committed)
├── agents/
│   ├── orchestrator.py        # Agent routing + StrategyBrief dataclass
│   ├── research_agent.py      # Pattern extraction + Strategy Brief engine
│   └── action_agent.py        # Socratic interaction handler
├── knowledge/
│   ├── patterns.json          # 40+ DSA paradigms with metadata
│   └── pattern_matcher.py     # Keyword → pattern parsing logic
├── executor/
│   ├── python_runner.py       # Isolated subprocess execution
│   ├── java_runner.py         # javac compilation + JVM runtime
│   └── sandbox.py             # Temp workspace + network blocker
├── prompts/
│   ├── research_prompt.txt    # Algorithmic pattern identification prompt
│   └── mentor_prompt.txt      # Socratic persona + output filters
├── ui/
│   ├── chat_panel.py          # Left panel: conversation stream
│   └── code_panel.py          # Right panel: code editor + console
└── tests/
    ├── test_agents.py         # Agent state flow tests
    └── test_executor.py       # Sandbox + malicious code termination tests
```

---

## 🧩 Algorithmic Knowledge Matrix (40+ Paradigms)

**Arrays, Strings & Sorting**
`Sliding Window` · `Two Pointers` · `Fast & Slow Pointers` · `Prefix Sum` · `Binary Search` · `Merge/Quick Sort` · `Counting Sort`

**Graphs, Trees & Lists**
`BFS & DFS` · `Kruskal & Prim MST` · `Topological Sort` · `Dijkstra's Shortest Path` · `Union-Find` · `Tree Traversals & LCA` · `Linked List Mutation`

**DP & Advanced Paradigms**
`Memoization / Tabulation` · `0/1 & Unbounded Knapsack` · `Longest Common Subsequence` · `Backtracking` · `Greedy Optimizations` · `Monotonic Stacks/Queues` · `Trie Structure Matching`

---

## 🛡️ Security & Socratic Guardrails

| Defense | Implementation |
|---------|---------------|
| **Network Isolation** | Execution sandbox blocks all socket requests at runtime |
| **Hard Timeout** | 5-second watchdog terminates infinite loops |
| **Code Leak Filter** | Regex scanner strips code from LLM output until benchmarks unlock |
| **Progressive Hints** | Hints revealed one at a time based on conversation state |

---

## 🚀 Setup & Launch

**Requirements:** Python 3.10+, Java JDK 17+

```bash
# 1. Clone
git clone https://github.com/AnamikaShah95/dsa-mentor-agent.git
cd dsa-mentor-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
# Create .env file:
LLM_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash

# 4. Launch
streamlit run main.py
```

App runs at → `http://localhost:8501`

---

## 🗓️ Development Roadmap

| Phase | Days | Focus |
|-------|------|-------|
| Core Logic & Intelligence | Day 1–3 | Architecture, data contracts, mock pipeline |
| Pattern Knowledge Integration | Day 4–6 | 40+ paradigms, keyword parsing, API wrapping |
| Polyglot Execution Engine | Day 7–9 | Python sandbox, Java JVM, timeout defense |
| UI, Testing & Polish | Day 10–13 | Streamlit panels, integration tests, final review |
| **Capstone Submission** | **July 11, 2026** | **Delivered** ✅ |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Gemini 2.5 Flash via `langchain-google-genai` |
| Agent Framework | LangChain |
| Frontend | Streamlit |
| Code Execution | Python `subprocess` + Java `javac`/JVM |
| Environment | Python 3.13, Windows/PowerShell |

---

## 👩‍💻 Author

**Anamika Shah** — B.Tech CSE  
Internship Capstone Project · Released July 11, 2026

---

*Built with the belief that the best way to learn DSA is to be asked the right question at the right time.*
