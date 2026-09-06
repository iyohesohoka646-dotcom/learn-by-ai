#!/usr/bin/env python3
"""Install the bundled Learn by AI skill without overwriting existing files."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


SKILL_NAME = "learn-by-ai"
REPOSITORY_ROOT = Path(__file__).resolve().parent
SOURCE = REPOSITORY_ROOT / "skill" / SKILL_NAME


def configure_portable_stdio() -> None:
    """Prevent narrow console encodings from crashing on installation paths."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(errors="backslashreplace")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install Learn by AI into an Agent Skills directory."
    )
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument(
        "--target",
        type=Path,
        help="Agent skills root; the installer creates <target>/learn-by-ai",
    )
    destination.add_argument(
        "--codex",
        action="store_true",
        help="Install into $CODEX_HOME/skills or ~/.codex/skills",
    )
    destination.add_argument(
        "--agents",
        action="store_true",
        help="Install into ~/.agents/skills for agents that support the shared location",
    )
    destination.add_argument(
        "--claude",
        action="store_true",
        help="Install into ~/.claude/skills for Claude Code",
    )
    destination.add_argument(
        "--cursor",
        action="store_true",
        help="Install into ~/.cursor/skills for Cursor",
    )
    destination.add_argument(
        "--opencode",
        action="store_true",
        help="Install into ~/.config/opencode/skills for OpenCode",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved destination without copying files",
    )
    return parser.parse_args()


def codex_skills_root() -> Path:
    configured = os.environ.get("CODEX_HOME")
    codex_home = Path(configured).expanduser() if configured else Path.home() / ".codex"
    return codex_home / "skills"


def target_skills_root(args: argparse.Namespace) -> Path:
    if args.codex:
        return codex_skills_root()
    if args.agents:
        return Path.home() / ".agents" / "skills"
    if args.claude:
        return Path.home() / ".claude" / "skills"
    if args.cursor:
        return Path.home() / ".cursor" / "skills"
    if args.opencode:
        return Path.home() / ".config" / "opencode" / "skills"
    return args.target.expanduser()


def main() -> int:
    configure_portable_stdio()
    args = parse_args()
    if not (SOURCE / "SKILL.md").is_file():
        print(f"error: bundled skill is missing: {SOURCE}", file=sys.stderr)
        return 2

    target_root = target_skills_root(args)
    destination = target_root.resolve() / SKILL_NAME

    print(f"Source: {SOURCE}")
    print(f"Destination: {destination}")
    if args.dry_run:
        return 0

    if destination.exists():
        print(f"error: refusing to overwrite existing installation: {destination}", file=sys.stderr)
        return 3

    target_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, destination)
    print(f"Installed {SKILL_NAME}. Restart or reload the agent so it can discover the skill.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
