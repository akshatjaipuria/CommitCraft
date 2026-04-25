import subprocess
import json
import os

def _run_git(args: list, repo_path: str) -> str:
    """
    Internal helper to execute git commands safely.
    
    Args:
        args: List of git arguments (e.g., ["status", "-s"])
        repo_path: Absolute path to the git repository
        
    Returns:
        Standard output of the command or an error message.
    """
    try:
        # 0x08000000 = CREATE_NO_WINDOW (Prevents console popups on Windows)
        result = subprocess.run(
            ["git"] + args,
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            creationflags=0x08000000
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Git Error: {e.stderr.strip()}"
    except Exception as e:
        return f"System Error: {str(e)}"

def get_staged_diff(repo_path: str) -> str:
    """Retrieves the full diff of all staged changes."""
    return _run_git(["diff", "--staged"], repo_path)

def get_commit_context(repo_path: str) -> str:
    """Retrieves the last 5 commit messages to help the agent match project style."""
    return _run_git(["log", "-n", "5", "--pretty=format:%s"], repo_path)

def get_git_status(repo_path: str) -> str:
    """Retrieves the current branch name and a list of changed files."""
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], repo_path)
    status = _run_git(["status", "-s"], repo_path)
    return json.dumps({
        "branch": branch,
        "status": status
    })

# Map of tool names to their corresponding python functions for the agentic loop
tools_map = {
    "get_staged_diff": get_staged_diff,
    "get_commit_context": get_commit_context,
    "get_git_status": get_git_status
}
