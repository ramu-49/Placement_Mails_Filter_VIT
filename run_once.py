"""
Entry point for GitHub Actions (or any scheduler that runs the script
fresh each time, instead of keeping a process alive 24/7).

Runs exactly one inbox check, then exits. GitHub Actions will call this
on a schedule (e.g. every 15 minutes) instead of main.py's infinite loop.
"""

from main import run_one_check

if __name__ == "__main__":
    run_one_check()