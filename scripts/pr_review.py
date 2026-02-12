#!/usr/bin/env python3
"""PR Review Validation Script

This script runs validation checks on PR changes, including:
- Production API smoke tests
- Linting (ruff)
- Type checking (mypy)
- Filter and shape conformance (when manifest is available)
- Full test suite

Automatically detects PR context from:
- GitHub Actions environment variables
- GitHub CLI (gh)
- Git branch information

Usage:
    uv run python scripts/pr_review.py --mode smoke
    uv run python scripts/pr_review.py --mode quick
    uv run python scripts/pr_review.py --mode full
    uv run python scripts/pr_review.py --mode production
    uv run python scripts/pr_review.py --pr-number 123

Validation Modes:
    smoke      - Production API smoke tests only
    quick      - Linting + type checking (no tests)
    full       - All checks (linting + type checking + all tests)
    production - Production API smoke tests + linting + type checking
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env")
except ImportError:
    pass  # dotenv is optional

ValidationMode = Literal["smoke", "quick", "full", "production"]


@dataclass
class PRInfo:
    """Information about a pull request"""

    number: int | None = None
    title: str | None = None
    author: str | None = None
    base_branch: str = "main"
    head_branch: str | None = None
    url: str | None = None
    state: str | None = None


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_success(text: str) -> None:
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str) -> None:
    """Print an error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text: str) -> None:
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def run_command(cmd: list[str], description: str, check: bool = True) -> int:
    """Run a command and return its exit code"""
    print(f"Running: {description}...")
    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        print()
        if result.returncode == 0:
            print_success(f"{description} passed")
        else:
            print_error(f"{description} failed")
        return result.returncode
    except FileNotFoundError as e:
        print_error(f"Command not found: {e}")
        return 1
    except Exception as e:
        print_error(f"Error running command: {e}")
        return 1


def detect_pr_from_github_actions() -> PRInfo | None:
    """Detect PR information from GitHub Actions environment variables"""
    pr_number = os.getenv("GITHUB_PR_NUMBER")
    if not pr_number:
        # Try alternative env var format
        pr_number = os.getenv("PR_NUMBER")
    if not pr_number:
        # Check if we're in a PR context
        event_path = os.getenv("GITHUB_EVENT_PATH")
        if event_path and Path(event_path).exists():
            try:
                with open(event_path) as f:
                    event_data = json.load(f)
                    if "pull_request" in event_data:
                        pr = event_data["pull_request"]
                        return PRInfo(
                            number=pr.get("number"),
                            title=pr.get("title"),
                            author=pr.get("user", {}).get("login"),
                            base_branch=pr.get("base", {}).get("ref", "main"),
                            head_branch=pr.get("head", {}).get("ref"),
                            url=pr.get("html_url"),
                            state=pr.get("state"),
                        )
            except Exception as e:
                print(f"Warning: Could not read/parse GitHub event file: {e}", file=sys.stderr)

    if pr_number:
        try:
            return PRInfo(number=int(pr_number))
        except ValueError:
            pass

    return None


def get_pr_info_from_gh_cli(pr_number: int | None = None) -> PRInfo | None:
    """Get PR information using GitHub CLI (gh)"""
    try:
        # Check if gh CLI is available
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            return None

        # Get current PR or specific PR number
        if pr_number:
            cmd = ["gh", "pr", "view", str(pr_number), "--json", "number,title,author,baseRefName,headRefName,url,state"]
        else:
            cmd = ["gh", "pr", "view", "--json", "number,title,author,baseRefName,headRefName,url,state"]

        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            try:
                pr_data = json.loads(result.stdout)
                return PRInfo(
                    number=pr_data.get("number"),
                    title=pr_data.get("title"),
                    author=pr_data.get("author", {}).get("login"),
                    base_branch=pr_data.get("baseRefName", "main"),
                    head_branch=pr_data.get("headRefName"),
                    url=pr_data.get("url"),
                    state=pr_data.get("state"),
                )
            except (json.JSONDecodeError, KeyError):
                pass
    except FileNotFoundError:
        # gh CLI not available - this is expected in some environments
        pass
    except Exception as e:
        print(f"Warning: Error getting PR info from gh CLI: {e}", file=sys.stderr)

    return None


def detect_pr_from_branch() -> PRInfo | None:
    """Try to detect PR from current branch name or git config"""
    try:
        # Get current branch
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            # Try to get PR info for this branch
            return get_pr_info_from_gh_cli(None)
    except Exception as e:
        print(f"Warning: Error detecting PR from branch: {e}", file=sys.stderr)

    return None


def get_pr_info(pr_number: int | None = None) -> PRInfo | None:
    """Get PR information from various sources"""
    # Try GitHub Actions first
    pr_info = detect_pr_from_github_actions()
    if pr_info:
        return pr_info

    # Try GitHub CLI
    pr_info = get_pr_info_from_gh_cli(pr_number)
    if pr_info:
        return pr_info

    # Try to detect from branch
    if not pr_number:
        pr_info = detect_pr_from_branch()
        if pr_info:
            return pr_info

    return None


def get_changed_files(base_branch: str = "main") -> list[str]:
    """Get list of changed Python files compared to base branch"""
    try:
        # Check if we're in a git repository
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=project_root,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            return []

        # Get changed files
        result = subprocess.run(
            ["git", "diff", "--name-only", f"origin/{base_branch}...HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            # Try without origin prefix
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{base_branch}...HEAD"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False,
            )

        if result.returncode != 0:
            # Fallback to working directory changes
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False,
            )

        changed_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
        python_files = [f for f in changed_files if f.endswith(".py")]

        return python_files
    except Exception as e:
        print_warning(f"Could not detect changed files: {e}")
        return []


def run_linting(files: list[str] | None = None) -> int:
    """Run ruff linting"""
    cmd = ["uv", "run", "ruff", "check", "tango/"]
    if files:
        # Only check changed files
        cmd.extend(files)
    return run_command(cmd, "Linting (ruff)")


def run_formatting_check(files: list[str] | None = None) -> int:
    """Check code formatting"""
    cmd = ["uv", "run", "ruff", "format", "--check", "tango/"]
    if files:
        # Only check changed files
        cmd.extend(files)
    return run_command(cmd, "Formatting check (ruff format)")


def run_type_checking(files: list[str] | None = None) -> int:
    """Run mypy type checking"""
    cmd = ["uv", "run", "mypy", "tango/"]
    if files:
        # Only check changed files (mypy needs directories)
        # For simplicity, we'll check the whole tango/ directory
        pass
    return run_command(cmd, "Type checking (mypy)")


def run_production_tests() -> int:
    """Run production API smoke tests"""
    api_key = os.getenv("TANGO_API_KEY")
    if not api_key:
        print_warning("TANGO_API_KEY not set - skipping production tests")
        print("Set it with: export TANGO_API_KEY=your-api-key")
        return 0  # Don't fail if API key is missing

    cmd = ["uv", "run", "python", "scripts/test_production.py"]
    return run_command(cmd, "Production API smoke tests", check=False)


def run_conformance_check() -> int:
    """Run filter and shape conformance. Skips if manifest not found."""
    manifest_path = os.getenv("TANGO_CONTRACT_MANIFEST")
    if not manifest_path:
        manifest_path = str(project_root / "tango-api" / "contracts" / "filter_shape_contract.json")
    path = Path(manifest_path)
    if not path.exists():
        print_warning("Conformance manifest not found - skipping filter/shape conformance")
        print(f"  Expected: {path}")
        print("  Set TANGO_CONTRACT_MANIFEST or clone tango repo as tango-api/ (see scripts/README.md)")
        return 0  # Don't fail when manifest is missing

    cmd = [
        "uv", "run", "python", "scripts/check_filter_shape_conformance.py",
        "--manifest", manifest_path,
    ]
    return run_command(cmd, "Filter and shape conformance", check=False)


def run_all_tests() -> int:
    """Run full test suite"""
    cmd = ["uv", "run", "pytest", "tests/", "-m", "not integration"]
    return run_command(cmd, "Unit tests", check=False)


def run_integration_tests() -> int:
    """Run integration tests"""
    cmd = ["uv", "run", "pytest", "tests/integration/"]
    return run_command(cmd, "Integration tests", check=False)


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run validation checks for PR review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["smoke", "quick", "full", "production"],
        default="production",
        help="Validation mode (default: production)",
    )
    parser.add_argument(
        "--base-branch",
        default=None,
        help="Base branch to compare against (auto-detected from PR if not specified)",
    )
    parser.add_argument(
        "--changed-files-only",
        action="store_true",
        help="Only check changed files (for linting/formatting)",
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        default=None,
        help="PR number to review (auto-detected if not specified)",
    )

    args = parser.parse_args()

    # Detect PR information
    pr_info = get_pr_info(args.pr_number)

    # Determine base branch
    base_branch = args.base_branch
    if not base_branch and pr_info:
        base_branch = pr_info.base_branch
    if not base_branch:
        base_branch = "main"

    # Print PR information if available
    if pr_info and pr_info.number:
        print_header(f"PR #{pr_info.number} Review")
        if pr_info.title:
            print(f"{Colors.BOLD}Title:{Colors.RESET} {pr_info.title}")
        if pr_info.author:
            print(f"{Colors.BOLD}Author:{Colors.RESET} {pr_info.author}")
        if pr_info.base_branch:
            print(f"{Colors.BOLD}Base Branch:{Colors.RESET} {pr_info.base_branch}")
        if pr_info.head_branch:
            print(f"{Colors.BOLD}Head Branch:{Colors.RESET} {pr_info.head_branch}")
        if pr_info.url:
            print(f"{Colors.BOLD}URL:{Colors.RESET} {pr_info.url}")
        print()
    else:
        print_header(f"PR Review Validation - Mode: {args.mode}")
        if args.pr_number:
            print_warning(f"Could not fetch PR #{args.pr_number} information")
            print("Make sure you're authenticated with GitHub CLI (gh auth login)")
            print()

    # Get changed files if requested
    changed_files: list[str] | None = None
    if args.changed_files_only or pr_info:
        changed_files = get_changed_files(base_branch)
        if changed_files:
            print(f"{Colors.BOLD}Changed Python files: {len(changed_files)}{Colors.RESET}")
            for f in changed_files[:10]:  # Show first 10
                print(f"  - {f}")
            if len(changed_files) > 10:
                print(f"  ... and {len(changed_files) - 10} more")
        else:
            print("No changed Python files detected")
        print()

    exit_codes: list[int] = []

    # Run validations based on mode
    # Auto-enable changed-files-only if PR is detected
    use_changed_files = args.changed_files_only or (pr_info is not None)

    if args.mode == "smoke":
        exit_codes.append(run_production_tests())

    elif args.mode == "quick":
        exit_codes.append(run_formatting_check(changed_files if use_changed_files else None))
        exit_codes.append(run_linting(changed_files if use_changed_files else None))
        exit_codes.append(run_type_checking(changed_files if use_changed_files else None))

    elif args.mode == "full":
        exit_codes.append(run_formatting_check())
        exit_codes.append(run_linting())
        exit_codes.append(run_type_checking())
        exit_codes.append(run_conformance_check())
        exit_codes.append(run_all_tests())
        exit_codes.append(run_integration_tests())

    elif args.mode == "production":
        exit_codes.append(run_formatting_check(changed_files if use_changed_files else None))
        exit_codes.append(run_linting(changed_files if use_changed_files else None))
        exit_codes.append(run_type_checking(changed_files if use_changed_files else None))
        exit_codes.append(run_conformance_check())
        exit_codes.append(run_production_tests())

    # Summary
    print_header("Summary")
    total_failed = sum(1 for code in exit_codes if code != 0)
    total_passed = len(exit_codes) - total_failed

    print(f"Total checks: {len(exit_codes)}")
    print_success(f"Passed: {total_passed}")
    if total_failed > 0:
        print_error(f"Failed: {total_failed}")
        if pr_info and pr_info.url:
            print(f"\n{Colors.BOLD}PR URL:{Colors.RESET} {pr_info.url}")
        return 1
    else:
        print_success("All checks passed!")
        if pr_info and pr_info.url:
            print(f"\n{Colors.BOLD}PR URL:{Colors.RESET} {pr_info.url}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
