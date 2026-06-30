# executor/python_runner.py
"""
Day 7: Python execution engine
Runs student Python code in an isolated subprocess with a hard timeout.
"""

import subprocess
import sys
import os

import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from executor.sandbox import Sandbox

TIMEOUT_SECONDS = 5


def run_python_code(code: str, stdin_input: str = "") -> dict:
    """
    Executes Python code in an isolated subprocess.
    Returns a dict with stdout, stderr, exit_code, timed_out, and success.
    """
    with Sandbox() as sb:
        filepath = sb.write_file("solution.py", code)

        try:
            result = subprocess.run(
                [sys.executable, filepath],
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                cwd=sb.workspace_path,
                env={"PATH": os.environ.get("PATH", "")},  # minimal env, no extra secrets
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "timed_out": False,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {TIMEOUT_SECONDS} seconds. "
                          f"Check for infinite loops.",
                "exit_code": -1,
                "timed_out": True,
                "success": False
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "exit_code": -1,
                "timed_out": False,
                "success": False
            }


# ── Test ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("DAY 7: PYTHON RUNNER TEST")
    print("=" * 60)

    test_cases = [
        {
            "name": "Valid code",
            "code": "print('Hello, DSA Mentor!')\nresult = sum([1, 2, 3, 4, 5])\nprint(f'Sum: {result}')"
        },
        {
            "name": "Code with a runtime error",
            "code": "x = 10\ny = 0\nprint(x / y)"
        },
        {
            "name": "Infinite loop (should timeout)",
            "code": "while True:\n    pass"
        },
        {
            "name": "Code that reads stdin",
            "code": "name = input()\nprint(f'Hello, {name}!')"
        }
    ]

    for test in test_cases:
        print(f"\n--- {test['name']} ---")
        stdin = "Anamika" if "stdin" in test["name"] else ""
        result = run_python_code(test["code"], stdin_input=stdin)
        print(f"  Success: {result['success']}")
        print(f"  Timed out: {result['timed_out']}")
        print(f"  Stdout: {result['stdout'].strip()}")
        if result['stderr']:
            print(f"  Stderr: {result['stderr'].strip()[:150]}")

    print("\n" + "=" * 60)
    print("Python runner working correctly!")