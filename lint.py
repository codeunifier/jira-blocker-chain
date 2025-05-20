#!/usr/bin/env python3
"""
Lint script to run all linting tools on the project.
"""
import os
import subprocess
import sys


def run_command(command, description):
    """Run a command and print its output."""
    print(f"\n=== Running {description} ===")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"Errors:\n{result.stderr}")
    return result.returncode == 0


def main():
    """Run all linting tools."""
    success = True

    # Get Python files
    py_files = []
    for root, _, files in os.walk("."):
        if "/.venv/" in root or "/__pycache__/" in root or "/output/" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))

    # Run isort
    if not run_command(f"isort {' '.join(py_files)}", "isort"):
        success = False

    # Run black
    if not run_command(f"black {' '.join(py_files)}", "black"):
        success = False

    # Run flake8
    if not run_command(f"flake8 {' '.join(py_files)}", "flake8"):
        success = False

    # Run mypy
    if not run_command("mypy .", "mypy"):
        success = False

    if success:
        print("\n✅ All linting checks passed!")
        return 0
    else:
        print("\n❌ Some linting checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
