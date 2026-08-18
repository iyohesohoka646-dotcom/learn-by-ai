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


def main() -> int:
    args = parse_args()
    if not (SOURCE / "SKILL.md").is_file():
        print(f"error: bundled skill is missing: {SOURCE}", file=sys.stderr)
        return 2

    target_root = codex_skills_root() if args.codex else args.target.expanduser()
    destination = target_root.resolve() / SKILL_NAME

    if destination.exists():
        print(f"error: refusing to overwrite existing installation: {destination}", file=sys.stderr)
        return 3

    print(f"Source: {SOURCE}")
    print(f"Destination: {destination}")
    if args.dry_run:
        return 0

    target_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, destination)
    print(f"Installed {SKILL_NAME}. Restart or reload the agent so it can discover the skill.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
