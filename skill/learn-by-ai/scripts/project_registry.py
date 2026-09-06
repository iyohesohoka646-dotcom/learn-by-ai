#!/usr/bin/env python3
"""Maintain and query the local Learn by AI project registry."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_FILES = {
    "project.yaml",
    "resource-index.yaml",
    "knowledge-graph.yaml",
    "learner-state.yaml",
    "evidence.jsonl",
    "checkpoint.md",
}
IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "vendor",
}


def configure_portable_stdio() -> None:
    """Prevent narrow console encodings from crashing on project names and paths."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(errors="backslashreplace")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def registry_path(override: str | Path | None = None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    configured = os.environ.get("LEARN_BY_AI_HOME")
    base = Path(configured).expanduser() if configured else Path.home() / ".learn-by-ai"
    return base.resolve() / "projects.json"


def empty_registry() -> dict[str, Any]:
    return {"schema_version": 1, "projects": []}


def load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_registry()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("projects"), list):
        raise ValueError(f"invalid registry structure: {path}")
    data.setdefault("schema_version", 1)
    return data


def write_registry(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix="projects-",
            suffix=".tmp",
            delete=False,
        ) as stream:
            stream.write(payload)
            temporary_name = stream.name
        os.replace(temporary_name, path)
    finally:
        if temporary_name:
            temporary = Path(temporary_name)
            if temporary.exists():
                temporary.unlink()


def parse_yaml_scalar(raw: str) -> Any:
    value = raw.strip()
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        if value in {"null", "~"}:
            return None
        return value.strip("'\"")


def read_project_metadata(directory: Path) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for line in (directory / "project.yaml").read_text(encoding="utf-8").splitlines():
        if not line or line[0].isspace() or ":" not in line or line.lstrip().startswith("#"):
            continue
        key, raw = line.split(":", 1)
        if key in {"project_id", "name", "goal", "aliases", "tags", "updated_at", "current_node"}:
            metadata[key] = parse_yaml_scalar(raw)
    return metadata


def project_health(directory: Path) -> tuple[bool, list[str]]:
    missing = sorted(name for name in STATE_FILES if not (directory / name).is_file())
    return not missing, missing


def normalized(value: str) -> str:
    return " ".join(re.findall(r"[\w]+", value.casefold(), flags=re.UNICODE))


def as_strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if value is None:
        return []
    return [str(value)]


def build_entry(
    directory: Path,
    *,
    name: str | None = None,
    goal: str | None = None,
    aliases: list[str] | None = None,
    tags: list[str] | None = None,
    current_node: str | None = None,
) -> dict[str, Any]:
    directory = directory.expanduser().resolve()
    valid, missing = project_health(directory)
    if not valid:
        raise ValueError(f"incomplete learning project at {directory}; missing: {', '.join(missing)}")
    metadata = read_project_metadata(directory)
    now = utc_now()
    return {
        "project_id": str(metadata.get("project_id") or directory.name),
        "name": name or str(metadata.get("name") or directory.name),
        "path": str(directory),
        "aliases": aliases if aliases is not None else as_strings(metadata.get("aliases")),
        "goal": goal or str(metadata.get("goal") or ""),
        "tags": tags if tags is not None else as_strings(metadata.get("tags")),
        "current_node": current_node if current_node is not None else metadata.get("current_node"),
        "project_updated_at": metadata.get("updated_at"),
        "last_verified_at": now,
    }


def register_project(
    directory: str | Path,
    *,
    registry: str | Path | None = None,
    name: str | None = None,
    goal: str | None = None,
    aliases: list[str] | None = None,
    tags: list[str] | None = None,
    current_node: str | None = None,
) -> Path:
    path = registry_path(registry)
    entry = build_entry(
        Path(directory),
        name=name,
        goal=goal,
        aliases=aliases,
        tags=tags,
        current_node=current_node,
    )
    data = load_registry(path)
    entries = [item for item in data["projects"] if item.get("path") != entry["path"]]
    entries.append(entry)
    data["projects"] = sorted(entries, key=lambda item: (normalized(str(item.get("name", ""))), item["path"]))
    write_registry(path, data)
    return path


def discover_projects(root: Path, max_depth: int) -> list[dict[str, Any]]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        return []
    found: list[dict[str, Any]] = []
    root_depth = len(root.parts)
    for current, directories, files in os.walk(root):
        current_path = Path(current)
        depth = len(current_path.parts) - root_depth
        directories[:] = [name for name in directories if name not in IGNORED_DIRECTORIES]
        if depth >= max_depth:
            directories[:] = []
        if STATE_FILES.issubset(files):
            try:
                found.append(build_entry(current_path))
            except (OSError, UnicodeError, ValueError):
                continue
            directories[:] = []
    return found


def match_score(query: str, entry: dict[str, Any]) -> int:
    query_norm = normalized(query)
    if not query_norm:
        return 0
    names = [entry.get("name", ""), *as_strings(entry.get("aliases"))]
    tags = as_strings(entry.get("tags"))
    names_norm = [normalized(str(value)) for value in names if str(value).strip()]
    tags_norm = [normalized(value) for value in tags]
    if query_norm in names_norm:
        return 100
    if any(query_norm in value or value in query_norm for value in names_norm if value):
        return 82
    if query_norm in tags_norm:
        return 72
    searchable = normalized(" ".join([*map(str, names), *tags, str(entry.get("goal", ""))]))
    query_tokens = set(query_norm.split())
    searchable_tokens = set(searchable.split())
    overlap = len(query_tokens & searchable_tokens)
    if overlap:
        return 40 + round(35 * overlap / len(query_tokens))
    if query_norm in searchable:
        return 55
    return 0


def find_projects(
    query: str,
    *,
    registry: str | Path | None = None,
    scan_roots: list[str] | None = None,
    max_depth: int = 5,
    include_invalid: bool = False,
) -> list[dict[str, Any]]:
    path = registry_path(registry)
    data = load_registry(path)
    by_path: dict[str, dict[str, Any]] = {}
    for item in data["projects"]:
        candidate = dict(item)
        directory = Path(str(candidate.get("path", ""))).expanduser()
        valid, missing = project_health(directory)
        candidate.update({"valid": valid, "missing_files": missing, "source": "registry"})
        by_path[str(directory.resolve())] = candidate
    for raw_root in scan_roots or []:
        for candidate in discover_projects(Path(raw_root), max_depth):
            candidate.update({"valid": True, "missing_files": [], "source": "scan"})
            by_path.setdefault(candidate["path"], candidate)
    matches: list[dict[str, Any]] = []
    for candidate in by_path.values():
        score = match_score(query, candidate)
        if score and (candidate["valid"] or include_invalid):
            candidate["score"] = score
            matches.append(candidate)
    matches.sort(key=lambda item: normalized(str(item.get("name", ""))))
    matches.sort(key=lambda item: str(item.get("project_updated_at") or ""), reverse=True)
    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Register and find Learn by AI learning projects.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register = subparsers.add_parser("register", help="Register or refresh one complete learning project.")
    register.add_argument("path")
    register.add_argument("--registry")
    register.add_argument("--name")
    register.add_argument("--goal")
    register.add_argument("--alias", action="append", default=None)
    register.add_argument("--tag", action="append", default=None)
    register.add_argument("--current-node")

    find = subparsers.add_parser("find", help="Find projects by name, alias, goal, or tag.")
    find.add_argument("query")
    find.add_argument("--registry")
    find.add_argument("--scan-root", action="append", default=[])
    find.add_argument("--max-depth", type=int, default=5)
    find.add_argument("--include-invalid", action="store_true")

    listing = subparsers.add_parser("list", help="List registered projects and verify their state files.")
    listing.add_argument("--registry")
    listing.add_argument("--include-invalid", action="store_true")
    return parser


def main() -> int:
    configure_portable_stdio()
    args = build_parser().parse_args()
    try:
        if args.command == "register":
            path = register_project(
                args.path,
                registry=args.registry,
                name=args.name,
                goal=args.goal,
                aliases=args.alias,
                tags=args.tag,
                current_node=args.current_node,
            )
            print(json.dumps({"registered": str(Path(args.path).expanduser().resolve()), "registry": str(path)}, ensure_ascii=True))
            return 0
        if args.command == "find":
            matches = find_projects(
                args.query,
                registry=args.registry,
                scan_roots=args.scan_root,
                max_depth=args.max_depth,
                include_invalid=args.include_invalid,
            )
            print(json.dumps(matches, ensure_ascii=True, indent=2))
            return 0
        path = registry_path(args.registry)
        data = load_registry(path)
        output = []
        for item in data["projects"]:
            candidate = dict(item)
            valid, missing = project_health(Path(str(candidate.get("path", ""))).expanduser())
            candidate.update({"valid": valid, "missing_files": missing})
            if valid or args.include_invalid:
                output.append(candidate)
        print(json.dumps(output, ensure_ascii=True, indent=2))
        return 0
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
