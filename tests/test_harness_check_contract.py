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
