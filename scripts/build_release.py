#!/usr/bin/env python3
"""Build an uploadable .skill ZIP with the skill folder at archive root."""

from __future__ import annotations

import argparse
import shutil
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "learn-by-ai"
SOURCE = ROOT / "skill" / SKILL_NAME


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package Learn by AI as a .skill archive.")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "dist" / f"{SKILL_NAME}.skill",
        help="Output archive path",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not (SOURCE / "SKILL.md").is_file():
        raise SystemExit(f"error: missing {SOURCE / 'SKILL.md'}")

    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="learn-by-ai-package-") as temporary:
        archive_base = Path(temporary) / SKILL_NAME
        zip_path = Path(
            shutil.make_archive(
                str(archive_base),
                "zip",
                root_dir=SOURCE.parent,
                base_dir=SKILL_NAME,
            )
        )
        output.write_bytes(zip_path.read_bytes())

    with zipfile.ZipFile(output) as archive:
        required = f"{SKILL_NAME}/SKILL.md"
        if required not in archive.namelist():
            output.unlink(missing_ok=True)
            raise SystemExit(f"error: package is missing {required}")

    print(f"Built {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
