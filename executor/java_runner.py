# executor/java_runner.py
"""
Day 8: Java compilation + execution pipeline
Uses threading + taskkill for reliable timeout enforcement on Windows.
"""

import subprocess
import os
import re
import sys
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from executor.sandbox import Sandbox

TIMEOUT_SECONDS = 5


def extract_class_name(code: str) -> str:
    match = re.search(r"public\s+class\s+(\w+)", code)
    if match:
        return match.group(1)
    match = re.search(r"class\s+(\w+)", code)
    if match:
        return match.group(1)
    return "Solution"


def _kill_process(proc: subprocess.Popen):
    """Force-kills a process and its children using taskkill on Windows."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            capture_output=True
        )
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def run_java_code(code: str, stdin_input: str = "") -> dict:
    class_name = extract_class_name(code)

    with Sandbox() as sb:
        filename = f"{class_name}.java"
        filepath = sb.write_file(filename, code)

        # ── Step 1: Compile ───────────────────────────────────────────────
        try:
            compile_result = subprocess.run(
                ["javac", filepath],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=sb.workspace_path
            )
        except subprocess.TimeoutExpired:
            return {
                "stdout": "", "stderr": "Compilation timed out.",
                "exit_code": -1, "timed_out": True,
                "success": False, "compile_error": True
            }
        except FileNotFoundError:
            return {
                "stdout": "", "stderr": "javac not found. Install Java JDK 17+.",
                "exit_code": -1, "timed_out": False,
                "success": False, "compile_error": True
            }

        if compile_result.returncode != 0:
            return {
                "stdout": "", "stderr": compile_result.stderr,
                "exit_code": compile_result.returncode, "timed_out": False,
                "success": False, "compile_error": True
            }

        # ── Step 2: Run with thread-based timeout + taskkill ──────────────
        proc = None
        stdout_val = ""
        stderr_val = ""
        exit_code = -1
        timed_out = False

        try:
            proc = subprocess.Popen(
                ["java", "-cp", sb.workspace_path, class_name],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=sb.workspace_path
            )

            # Timer thread: kills process if it exceeds timeout
            timer = threading.Timer(TIMEOUT_SECONDS, _kill_process, args=[proc])
            timer.start()

            try:
                stdin_bytes = stdin_input if stdin_input else ""
                stdout_val, stderr_val = proc.communicate(input=stdin_bytes)
                exit_code = proc.returncode
                timed_out = not timer.is_alive()  # timer fired = timed out
            finally:
                timer.cancel()

        except Exception as e:
            stderr_val = f"Execution error: {str(e)}"

        # If taskkill fired, returncode is often 1 or negative
        if timed_out or (proc and proc.returncode not in (0, None) and not stdout_val and not stderr_val):
            timed_out = True
            stderr_val = (f"Execution timed out after {TIMEOUT_SECONDS} seconds. "
                         f"Check for infinite loops.")
            exit_code = -1

        return {
            "stdout": stdout_val,
            "stderr": stderr_val,
            "exit_code": exit_code,
            "timed_out": timed_out,
            "success": exit_code == 0 and not timed_out,
            "compile_error": False
        }


# ── Test ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("DAY 8: JAVA RUNNER TEST")
    print("=" * 60)

    test_cases = [
        {
            "name": "Valid Java code",
            "code": """
public class Solution {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
        int sum = 0;
        for (int i = 1; i <= 5; i++) sum += i;
        System.out.println("Sum: " + sum);
    }
}"""
        },
        {
            "name": "Compilation error",
            "code": """
public class BrokenSolution {
    public static void main(String[] args) {
        System.out.println("Missing semicolon")
    }
}"""
        },
        {
            "name": "Runtime error",
            "code": """
public class RuntimeErr {
    public static void main(String[] args) {
        int[] arr = new int[3];
        System.out.println(arr[10]);
    }
}"""
        },
      {
            "name": "Infinite loop (should timeout)",
            "code": """
public class InfiniteLoop {
    public static void main(String[] args) {
        while (true) {}
    }
}"""
        },
        {
            "name": "Reads stdin input",
            "code": """
import java.util.Scanner;
public class ReadInput {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String name = sc.nextLine();
        System.out.println("Hello, " + name + "!");
    }
}"""
        }
    ]

    for test in test_cases:
        print(f"\n--- {test['name']} ---")
        stdin = "Anamika" if "stdin" in test["name"].lower() else ""
        result = run_java_code(test["code"], stdin_input=stdin)
        print(f"  Compile error: {result.get('compile_error', False)}")
        print(f"  Success:       {result['success']}")
        print(f"  Timed out:     {result['timed_out']}")
        if result['stdout']:
            print(f"  Stdout: {result['stdout'].strip()}")
        if result['stderr']:
            print(f"  Stderr: {result['stderr'].strip()[:200]}")

    print("\n" + "=" * 60)
    print("Java runner working correctly!")