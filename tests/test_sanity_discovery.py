import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest


class TestSanityDiscovery(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent.parent
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.sanity_script = self.root / "scripts" / "sanity-check.sh"

        self._symlink(self.repo_root / "commands", self.root / "commands")
        self._symlink(self.repo_root / "templates", self.root / "templates")
        self._symlink(self.repo_root / "hooks", self.root / "hooks")
        self._symlink(self.repo_root / "docs", self.root / "docs")
        self._symlink(self.repo_root / "VERSION", self.root / "VERSION")
        self._symlink(self.repo_root / "technology.yaml", self.root / "technology.yaml")

        scripts_dir = self.root / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        for name in ["sanity-check.sh", "harness-status.py", "version-check.py"]:
            shutil.copy2(self.repo_root / "scripts" / name, scripts_dir / name)

        harness_dir = self.root / ".harness-eng"
        harness_dir.mkdir(parents=True, exist_ok=True)
        self._symlink(self.repo_root / ".harness-eng" / "agents", harness_dir / "agents")
        self._symlink(self.repo_root / ".harness-eng" / "internal-scripts", harness_dir / "internal-scripts")
        self._symlink(self.repo_root / ".harness-eng" / "VERSION", harness_dir / "VERSION")
        self._symlink(self.repo_root / ".harness-eng" / "CONSTITUTION.md", harness_dir / "CONSTITUTION.md")
        self._symlink(self.repo_root / ".harness-eng" / "BRD.md", harness_dir / "BRD.md")

        self.skills_dir = harness_dir / "skills"
        baseline_skill = self.skills_dir / "python"
        baseline_skill.mkdir(parents=True)
        (baseline_skill / "SKILL.md").write_text(
            "---\nname: python\ndescription: baseline test skill\n---\n",
            encoding="utf-8",
        )
        self.mock_skill_dir = self.skills_dir / "mockskilltest"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _symlink(self, source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(source, target_is_directory=source.is_dir())

    def test_dynamic_skills_discovery(self) -> None:
        self.mock_skill_dir.mkdir(parents=True, exist_ok=True)
        (self.mock_skill_dir / "SKILL.md").write_text(
            "---\nname: mockskilltest\ndescription: test skill\n---\n",
            encoding="utf-8",
        )

        actual_skills_count = len([path for path in self.skills_dir.iterdir() if path.is_dir()])
        env = os.environ.copy()
        env["SKIP_UNITTESTS"] = "1"
        res = subprocess.run(
            ["bash", str(self.sanity_script)],
            cwd=self.root,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

        expected_output_fragment = f"{actual_skills_count} skills verified"
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn(expected_output_fragment, res.stdout)


class TestEvidenceContractPolicy(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parent.parent

    def test_decision_points_reference_evidence_contract(self) -> None:
        required_files = (
            "commands/design.md",
            "commands/review-pre-build.md",
            "commands/build.md",
            "commands/review-pre-verify.md",
            "commands/verify.md",
            "templates/feature/design.md",
            "templates/feature/review-pre-build.md",
            "templates/feature/review-pre-verify.md",
            "templates/feature/verification.md",
        )
        for relative_path in required_files:
            with self.subTest(path=relative_path):
                content = (self.repo_root / relative_path).read_text(encoding="utf-8")
                normalized = content.lower().replace("_", " ")
                self.assertIn("evidence contract", normalized)

    def test_canonical_guidance_has_no_universal_test_mandate(self) -> None:
        canonical_files = (
            "AGENTS.md",
            "README.md",
            "templates/big-picture/CONSTITUTION.md",
        )
        prohibited = (
            "TDD Mandatory",
            'No feature is "done" without integration test',
            "Every story must use testable Given/When/Then format",
        )
        for relative_path in canonical_files:
            content = (self.repo_root / relative_path).read_text(encoding="utf-8")
            for phrase in prohibited:
                with self.subTest(path=relative_path, phrase=phrase):
                    self.assertNotIn(phrase, content)

    def test_release_policy_is_canonical_and_consumed(self) -> None:
        constitution = (self.repo_root / "templates/big-picture/CONSTITUTION.md").read_text(encoding="utf-8")
        release_command = (self.repo_root / "commands/release.md").read_text(encoding="utf-8")

        self.assertIn("release_policy:", constitution)
        self.assertIn("local_merge | pull_request", constitution)
        self.assertIn("read_release_policy", release_command)
        self.assertIn("push_target_branch_if_enabled", release_command)
        self.assertIn("push_release_tag_if_enabled", release_command)


if __name__ == "__main__":
    unittest.main()
