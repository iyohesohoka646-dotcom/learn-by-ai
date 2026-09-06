from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill" / "learn-by-ai"
STATE_FILES = {
    "project.yaml",
    "resource-index.yaml",
    "knowledge-graph.yaml",
    "learner-state.yaml",
    "evidence.jsonl",
    "checkpoint.md",
}


class PackageTests(unittest.TestCase):
    def test_skill_frontmatter_is_portable(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        frontmatter = text.split("---", 2)[1]
        keys = {
            line.split(":", 1)[0].strip()
            for line in frontmatter.splitlines()
            if ":" in line
        }
        self.assertEqual(keys, {"name", "description"})
        self.assertIn("name: learn-by-ai", frontmatter)

    def test_manifest_points_to_skill(self) -> None:
        manifest = json.loads((ROOT / "skill-package.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "learn-by-ai")
        self.assertTrue((ROOT / manifest["entrypoint"]).is_file())

    def test_skill_reference_links_resolve(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\[[^\]]+\]\((references/[^)]+)\)", text)
        self.assertTrue(links)
        for link in links:
            self.assertTrue((SKILL / link).is_file(), link)

    def test_release_archive_has_skill_folder_at_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "learn-by-ai.skill"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "build_release.py"),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
            self.assertIn("learn-by-ai/SKILL.md", names)
            self.assertIn("learn-by-ai/scripts/project_registry.py", names)
            self.assertIn("learn-by-ai/references/project-discovery.md", names)
            self.assertIn("learn-by-ai/references/retrieval-and-planning.md", names)
            self.assertNotIn("SKILL.md", names)

    def test_demo_project_is_complete_and_parseable(self) -> None:
        demo = ROOT / "examples" / "probability-distribution"
        self.assertTrue(STATE_FILES.issubset({path.name for path in demo.iterdir()}))
        for name in STATE_FILES:
            self.assertNotIn("{{", (demo / name).read_text(encoding="utf-8"))
        for line in (demo / "evidence.jsonl").read_text(encoding="utf-8").splitlines():
            json.loads(line)

    def test_generic_installer_copies_and_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "agent-skills"
            command = [sys.executable, str(ROOT / "install.py"), "--target", str(target)]
            first = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue((target / "learn-by-ai" / "SKILL.md").is_file())
            second = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(second.returncode, 3)
            self.assertIn("refusing to overwrite", second.stderr)

    def test_installer_resolves_supported_agent_locations(self) -> None:
        expected_suffixes = {
            "--agents": Path(".agents") / "skills" / "learn-by-ai",
            "--claude": Path(".claude") / "skills" / "learn-by-ai",
            "--cursor": Path(".cursor") / "skills" / "learn-by-ai",
            "--opencode": Path(".config") / "opencode" / "skills" / "learn-by-ai",
        }
        for flag, suffix in expected_suffixes.items():
            result = subprocess.run(
                [sys.executable, str(ROOT / "install.py"), flag, "--dry-run"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            destination_line = next(
                line for line in result.stdout.splitlines() if line.startswith("Destination:")
            )
            self.assertTrue(Path(destination_line.removeprefix("Destination:").strip()).is_absolute())
            self.assertTrue(destination_line.endswith(str(suffix)), destination_line)

    def test_initializer_creates_valid_state_non_destructively(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "learning-project"
            registry_home = Path(temporary) / "registry-home"
            environment = os.environ.copy()
            environment["LEARN_BY_AI_HOME"] = str(registry_home)
            command = [
                sys.executable,
                str(SKILL / "scripts" / "init_learning_project.py"),
                str(destination),
                "--name",
                "线性代数学习",
                "--goal",
                "Independently explain and apply eigenvalue decomposition",
                "--depth",
                "engineering",
                "--session-minutes",
                "90",
                "--alias",
                "linear algebra",
                "--tag",
                "mathematics",
            ]
            first = subprocess.run(command, capture_output=True, text=True, check=False, env=environment)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual({path.name for path in destination.iterdir()}, STATE_FILES)
            for path in destination.iterdir():
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("{{", text)
            for line in (destination / "evidence.jsonl").read_text(encoding="utf-8").splitlines():
                json.loads(line)
            registry = json.loads((registry_home / "projects.json").read_text(encoding="utf-8"))
            self.assertEqual(len(registry["projects"]), 1)
            self.assertEqual(Path(registry["projects"][0]["path"]), destination.resolve())

            find = subprocess.run(
                [
                    sys.executable,
                    str(SKILL / "scripts" / "project_registry.py"),
                    "find",
                    "linear algebra",
                ],
                capture_output=True,
                text=True,
                check=False,
                env=environment,
            )
            self.assertEqual(find.returncode, 0, find.stderr)
            matches = json.loads(find.stdout)
            self.assertEqual([item["name"] for item in matches], ["线性代数学习"])

            second = subprocess.run(command, capture_output=True, text=True, check=False, env=environment)
            self.assertEqual(second.returncode, 4)
            self.assertIn("refusing to overwrite", second.stderr)

    def test_registry_returns_parallel_projects_for_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            registry_home = Path(temporary) / "registry-home"
            environment = os.environ.copy()
            environment["LEARN_BY_AI_HOME"] = str(registry_home)
            initializer = SKILL / "scripts" / "init_learning_project.py"
            for folder, name, goal in (
                ("statistics-foundation", "Statistics foundation", "Master probability and inference"),
                ("statistics-research", "Statistics research", "Read modern high-dimensional statistics papers"),
            ):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(initializer),
                        str(Path(temporary) / folder),
                        "--name",
                        name,
                        "--goal",
                        goal,
                        "--alias",
                        "statistics",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                    env=environment,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

            find = subprocess.run(
                [
                    sys.executable,
                    str(SKILL / "scripts" / "project_registry.py"),
                    "find",
                    "statistics",
                ],
                capture_output=True,
                text=True,
                check=False,
                env=environment,
            )
            self.assertEqual(find.returncode, 0, find.stderr)
            matches = json.loads(find.stdout)
            self.assertEqual(len(matches), 2)
            self.assertTrue(all(item["valid"] for item in matches))


if __name__ == "__main__":
    unittest.main()
