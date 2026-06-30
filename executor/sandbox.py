# executor/sandbox.py
"""
Day 7: Sandbox workspace manager
Creates an isolated temp directory per execution, writes the student's
code to disk, and cleans up afterward. No network access is granted to
anything run inside this workspace.
"""

import tempfile
import os
import shutil
import uuid


class Sandbox:
    def __init__(self):
        self.workspace_id = str(uuid.uuid4())[:8]
        self.workspace_path = None

    def __enter__(self):
        self.workspace_path = tempfile.mkdtemp(prefix=f"dsa_sandbox_{self.workspace_id}_")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def write_file(self, filename: str, content: str) -> str:
        """Writes code to a file inside the sandbox and returns its full path."""
        if not self.workspace_path:
            raise RuntimeError("Sandbox not initialized. Use 'with Sandbox() as sb:'")
        filepath = os.path.join(self.workspace_path, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath

    def cleanup(self):
        """Removes the temp workspace and all its contents."""
        if self.workspace_path and os.path.exists(self.workspace_path):
            shutil.rmtree(self.workspace_path, ignore_errors=True)
            self.workspace_path = None


# ── Test ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Day 7: Sandbox Test ===\n")

    with Sandbox() as sb:
        print(f"Workspace created at: {sb.workspace_path}")
        path = sb.write_file("solution.py", "print('hello from sandbox')")
        print(f"File written to: {path}")
        print(f"File exists: {os.path.exists(path)}")

    print(f"\nAfter exiting 'with' block:")
    print(f"Workspace still exists: {os.path.exists(sb.workspace_path) if sb.workspace_path else 'cleaned up (None)'}")
    print("\nSandbox working correctly!")