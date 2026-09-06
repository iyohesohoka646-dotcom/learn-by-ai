#!/usr/bin/env python3
"""Create a non-destructive adaptive learning project from bundled templates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from project_registry import register_project


STATE_FILES = (
    "project.yaml",
    "resource-index.yaml",
    "knowledge-graph.yaml",
    "learner-state.yaml",
    "evidence.jsonl",
    "checkpoint.md",
)


def configure_portable_stdio() -> None:
    """Prevent narrow console encodings from crashing on project names and paths."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(errors="backslashreplace")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if slug:
        return slug
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]
    return f"learning-project-{digest}"


def yaml_string(value: str) -> str:
    # JSON double-quoted strings are valid YAML scalars and escape safely.
    return json.dumps(value, ensure_ascii=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize six human-readable files for an adaptive learning project."
    )
    parser.add_argument(
        "destination",
        nargs="?",
        default="learning-project",
        help="Project directory (default: ./learning-project)",
    )
    parser.add_argument("--name", help="Human-readable project name")
    parser.add_argument("--goal", required=True, help="Observable learning goal")
    parser.add_argument(
        "--depth",
        choices=("overview", "exam", "research", "engineering", "comprehensive"),
        default="comprehensive",
        help="Target depth (default: comprehensive)",
    )
    parser.add_argument(
        "--session-minutes",
        type=int,
        default=120,
        help="Normal effective session length (default: 120)",
    )
    parser.add_argument(
        "--alias",
        action="append",
        default=[],
        help="Alternate project name used for cross-session discovery; repeat as needed",
    )
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Discovery tag; repeat as needed",
    )
    parser.add_argument(
        "--registry",
        help="Override the local projects.json path",
    )
    parser.add_argument(
        "--no-register",
        action="store_true",
        help="Initialize project files without updating the cross-session registry",
    )
    return parser.parse_args()


def main() -> int:
    configure_portable_stdio()
    args = parse_args()
    if not 15 <= args.session_minutes <= 480:
        print("error: --session-minutes must be between 15 and 480", file=sys.stderr)
        return 2

    destination = Path(args.destination).expanduser().resolve()
    template_dir = Path(__file__).resolve().parent.parent / "assets" / "learning-project-template"
    missing_templates = [name for name in STATE_FILES if not (template_dir / name).is_file()]
    if missing_templates:
        print(
            "error: bundled template(s) missing: " + ", ".join(missing_templates),
            file=sys.stderr,
        )
        return 3

    conflicts = [name for name in STATE_FILES if (destination / name).exists()]
    if conflicts:
        print(
            "error: refusing to overwrite existing state file(s): " + ", ".join(conflicts),
            file=sys.stderr,
        )
        return 4

    now = datetime.now(timezone.utc).replace(microsecond=0)
    project_name = args.name or destination.name
    replacements = {
        "{{PROJECT_ID}}": yaml_string(slugify(project_name)),
        "{{PROJECT_NAME}}": yaml_string(project_name),
        "{{PROJECT_GOAL}}": yaml_string(args.goal),
        "{{PROJECT_ALIASES}}": json.dumps(args.alias, ensure_ascii=False),
        "{{PROJECT_TAGS}}": json.dumps(args.tag, ensure_ascii=False),
        "{{PROJECT_NAME_JSON}}": json.dumps(project_name, ensure_ascii=False),
        "{{PROJECT_GOAL_JSON}}": json.dumps(args.goal, ensure_ascii=False),
        "{{TARGET_DEPTH}}": yaml_string(args.depth),
        "{{SESSION_MINUTES}}": str(args.session_minutes),
        "{{CREATED_AT}}": yaml_string(now.isoformat().replace("+00:00", "Z")),
        "{{EVENT_ID_JSON}}": json.dumps(f"init-{now.strftime('%Y%m%dT%H%M%SZ')}"),
        "{{TIMESTAMP_JSON}}": json.dumps(now.isoformat().replace("+00:00", "Z")),
    }

    rendered: dict[str, str] = {}
    for name in STATE_FILES:
        content = (template_dir / name).read_text(encoding="utf-8")
        if name == "evidence.jsonl":
            content = "\n".join(line for line in content.splitlines() if line.strip()) + "\n"
        for marker, value in replacements.items():
            content = content.replace(marker, value)
        unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", content)))
        if unresolved:
            print(
                f"error: unresolved template marker(s) in {name}: {', '.join(unresolved)}",
                file=sys.stderr,
            )
            return 5
        rendered[name] = content

    destination.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    try:
        for name in STATE_FILES:
            path = destination / name
            with path.open("w", encoding="utf-8", newline="\n") as stream:
                stream.write(rendered[name])
            created.append(path)
    except Exception as exc:
        for path in created:
            try:
                path.unlink()
            except OSError:
                pass
        print(f"error: initialization failed; rolled back new files: {exc}", file=sys.stderr)
        return 6

    print(f"Initialized adaptive learning project: {destination}")
    for name in STATE_FILES:
        print(f"  - {name}")
    if not args.no_register:
        try:
            path = register_project(
                destination,
                registry=args.registry,
                name=project_name,
                goal=args.goal,
                aliases=args.alias,
                tags=args.tag,
            )
            print(f"Registered project for cross-session discovery: {path}")
        except Exception as exc:
            print(
                f"warning: project initialized, but registry update failed: {exc}",
                file=sys.stderr,
            )
    print("Next: index materials, build a sparse goal-aligned graph, and run a compact diagnostic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
