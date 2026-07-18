import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest


SCRIPT_NAMES = [
    "harness-check.py",
    "blocked-state.py",
    "traceability.py",
    "sensor-runner.py",
    "harness_layout.py",
]


class TestHarnessCheckContract(unittest.TestCase):
    def make_project(self) -> Path:
        root = Path(tempfile.mkdtemp())
        (root / "scripts").mkdir()
        for name in SCRIPT_NAMES:
            shutil.copy2(Path("scripts") / name, root / "scripts" / name)
        (root / ".harness-eng" / "phases" / "active" / "phase-test" / "features" / "F999-test").mkdir(parents=True)
        return root

    def run_check(self, root: Path, command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", "scripts/harness-check.py", command],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_creates_blocked_after_third_failure(self) -> None:
        root = self.make_project()
        feature = root / ".harness-eng" / "phases" / "active" / "phase-test" / "features" / "F999-test"
        (feature / "spec.md").write_text("# Spec\n", encoding="utf-8")
        (feature / "tasks.md").write_text("- [x] complete\n", encoding="utf-8")
        (root / "technology.yaml").write_text(
            "sensors:\n  - id: unit-tests\n    command: python3 -c 'print(1)'\n    required_before: verify\n    timeout: 5\n    evidence: logs\n",
            encoding="utf-8",
        )
        for _ in range(3):
            proc = self.run_check(root, "verify")
            self.assertNotEqual(proc.returncode, 0)
        blocked = feature / "BLOCKED.md"
        self.assertTrue(blocked.is_file())
        self.assertIn("Attempts: 3", blocked.read_text(encoding="utf-8"))

    def test_verify_blocks_on_missing_traceability(self) -> None:
        root = self.make_project()
        feature = root / ".harness-eng" / "phases" / "active" / "phase-test" / "features" / "F999-test"
        (feature / "spec.md").write_text(
            """```yaml
scenario_id: SCN-100
source_requirement: docs/backlog.md#z
provenance: Confirmed
given: g
when: w
then: t
evidence_strategy: verification.md
```
""",
            encoding="utf-8",
        )
        (feature / "tasks.md").write_text("- [x] unrelated task\n", encoding="utf-8")
        (feature / "review-pre-verify.md").write_text("# Review\n**Ref**: APPROVED\n", encoding="utf-8")
        (root / "technology.yaml").write_text(
            "sensors:\n  - id: unit-tests\n    command: python3 -c 'print(1)'\n    required_before: verify\n    timeout: 5\n    evidence: logs\n",
            encoding="utf-8",
        )
        proc = self.run_check(root, "verify")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Traceability incomplete", proc.stdout)

    def test_release_accepts_canonical_markdown_release_ref(self) -> None:
        root = self.make_project()
        feature = root / ".harness-eng" / "phases" / "active" / "phase-test" / "features" / "F999-test"
        (feature / "verification.md").write_text(
            "# Verification\n\n**Release Ref**: PENDING\n",
            encoding="utf-8",
        )

        proc = self.run_check(root, "release")

        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("Ready to release", proc.stdout)

    def test_release_rejects_non_pending_release_ref(self) -> None:
        root = self.make_project()
        feature = root / ".harness-eng" / "phases" / "active" / "phase-test" / "features" / "F999-test"
        (feature / "verification.md").write_text(
            "# Verification\n\n**Release Ref**: APPROVED\n",
            encoding="utf-8",
        )

        proc = self.run_check(root, "release")

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("not complete or not marked PENDING", proc.stdout)

    def test_validate_build_with_worktree_yaml(self) -> None:
        root = self.make_project()
        feature = root / ".harness-eng" / "phases" / "active" / "phase-test" / "features" / "F999-test"
        
        # Test M/L-level (default): fails when tasks/design/worktree.yaml missing
        proc = self.run_check(root, "build")
        self.assertNotEqual(proc.returncode, 0)

        # Write spec.md, design.md (approved), tasks.md
        (feature / "spec.md").write_text("# Spec\nworkflow_level: M/L\n", encoding="utf-8")
        (feature / "design.md").write_text("# Design\n**Ref**: APPROVED\n", encoding="utf-8")
        (feature / "tasks.md").write_text("- [ ] Task 1\n", encoding="utf-8")

        # Fails because worktree.yaml is missing
        proc = self.run_check(root, "build")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("worktree.yaml exists", proc.stdout)

        # Write worktree.yaml -> now passes
        (root / ".harness-eng" / "worktree.yaml").write_text("files: []\n", encoding="utf-8")
        proc = self.run_check(root, "build")
        self.assertEqual(proc.returncode, 0)

        # Test S-level: skips design/tasks/worktree.yaml checks, needs only spec.yaml/spec.md
        s_root = self.make_project()
        s_feature = s_root / ".harness-eng" / "phases" / "active" / "phase-test" / "features" / "F999-test"
        (s_feature / "spec.yaml").write_text("metadata:\n  workflow_level: S\n", encoding="utf-8")
        
        proc = self.run_check(s_root, "build")
        self.assertEqual(proc.returncode, 0)

    def test_validate_verify_skipping(self) -> None:
        # Test M/L-level (default): verify fails when review-pre-verify.md is missing
        root = self.make_project()
        (root / "technology.yaml").write_text("sensors:\n  - id: unit-tests\n    command: python3 -c 'print(1)'\n    required_before: verify\n    timeout: 5\n    evidence: logs\n", encoding="utf-8")
        feature = root / ".harness-eng" / "phases" / "active" / "phase-test" / "features" / "F999-test"
        (feature / "spec.md").write_text("# Spec\nworkflow_level: M/L\n", encoding="utf-8")
        (feature / "design.md").write_text("# Design\n**Ref**: APPROVED\n", encoding="utf-8")
        (feature / "tasks.md").write_text("- [ ] Task 1\n", encoding="utf-8")
        (root / ".harness-eng" / "worktree.yaml").write_text("files: []\n", encoding="utf-8")

        proc = self.run_check(root, "verify")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("review-pre-verify.md not approved", proc.stdout)

        # Test S-level: verify passes without review-pre-verify.md
        s_root = self.make_project()
        (s_root / "technology.yaml").write_text("sensors:\n  - id: unit-tests\n    command: python3 -c 'print(1)'\n    required_before: verify\n    timeout: 5\n    evidence: logs\n", encoding="utf-8")
        s_feature = s_root / ".harness-eng" / "phases" / "active" / "phase-test" / "features" / "F999-test"
        (s_feature / "spec.yaml").write_text("metadata:\n  workflow_level: S\n", encoding="utf-8")

        proc = self.run_check(s_root, "verify")
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
