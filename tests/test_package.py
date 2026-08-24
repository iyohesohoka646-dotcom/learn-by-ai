from __future__ import annotations

import json
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

    def test_initializer_creates_valid_state_non_destructively(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "learning-project"
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
            ]
            first = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual({path.name for path in destination.iterdir()}, STATE_FILES)
            for path in destination.iterdir():
                text = path.read_text(encoding="utf-8")
                self.assertNotIn("{{", text)
            for line in (destination / "evidence.jsonl").read_text(encoding="utf-8").splitlines():
                json.loads(line)
            second = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(second.returncode, 4)
            self.assertIn("refusing to overwrite", second.stderr)


if __name__ == "__main__":
    unittest.main()
