import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "init-boundary.py"


class TestInitCommandContract(unittest.TestCase):
    def test_init_binds_clarifications_and_stops(self):
        command = (ROOT / "commands" / "init.md").read_text()
        self.assertLess(command.index("read_canonical_agents"), command.index("bind_clarification_context"))
        self.assertIn("initialization input", command)
        self.assertIn("Create application implementation files", command)
        self.assertIn("stop_after_init", command)

    def test_agents_routes_by_harness_state(self):
        agents = (ROOT / "AGENTS.md").read_text()
        self.assertIn("User intent selects the desired outcome. Harness state selects the next permitted command.", agents)
        self.assertIn("earliest incomplete lifecycle command", agents)

    def test_health_is_lifecycle_aware(self):
        health = (ROOT / "commands" / "health.md").read_text()
        for status in ("PASS", "FAIL", "PENDING", "N/A"):
            self.assertIn(status, health)
        self.assertIn("derive_lifecycle_state", health)


class TestInitBoundary(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True)

    def test_allows_bootstrap_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("existing\n")
            baseline = root / ".harness-eng-init-baseline.json"
            self.assertEqual(self.run_script("snapshot", "--root", tmp, "--output", str(baseline)).returncode, 0)
            (root / ".harness-eng").mkdir()
            (root / ".harness-eng" / "CONSTITUTION.md").write_text("rules\n")
            (root / "AGENTS.md").write_text("instructions\n")
            result = self.run_script("check", "--root", tmp, "--baseline", str(baseline))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_created_application_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / ".harness-eng-init-baseline.json"
            self.run_script("snapshot", "--root", tmp, "--output", str(baseline))
            (root / "cmd" / "server").mkdir(parents=True)
            (root / "cmd" / "server" / "main.go").write_text("package main\n")
            result = self.run_script("check", "--root", tmp, "--baseline", str(baseline))
            self.assertEqual(result.returncode, 1)
            self.assertIn("cmd/server/main.go", result.stdout)

    def test_rejects_modified_brownfield_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "app.py"
            source.write_text("print('before')\n")
            baseline = root / ".harness-eng-init-baseline.json"
            self.run_script("snapshot", "--root", tmp, "--output", str(baseline))
            source.write_text("print('after')\n")
            result = self.run_script("check", "--root", tmp, "--baseline", str(baseline))
            self.assertEqual(result.returncode, 1)
            self.assertIn("app.py", result.stdout)


if __name__ == "__main__":
    unittest.main()
