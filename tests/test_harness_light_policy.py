import importlib.util
import os
import sys
import tempfile
from pathlib import Path
import unittest

# Add scripts/ directory to path so imports inside loaded modules resolve
sys.path.insert(0, str(Path("scripts").resolve()))

def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

harness_status = load_module(Path("scripts/harness-status.py"), "harness_status")
migrate_harness = load_module(Path("scripts/migrate-harness.py"), "migrate_harness")


class TestHarnessLightPolicy(unittest.TestCase):

    def test_to_yaml_serialization(self) -> None:
        data = {
            "state": "defined",
            "current_slice": "F301",
            "workflow_level": "S",
            "completed": ["Task 1", "Task 2"],
            "decisions": [{"id": "DEC-001", "ref": "spec.md"}],
            "empty_list": []
        }
        yaml_str = harness_status.to_yaml(data)
        self.assertIn('state: defined', yaml_str)
        self.assertIn('workflow_level: S', yaml_str)
        self.assertIn('  - Task 1', yaml_str)
        self.assertIn('  - id: DEC-001\n    ref: spec.md', yaml_str)
        self.assertIn('empty_list: []', yaml_str)

    def test_parse_markdown_metadata(self) -> None:
        content = """---
workflow_level: S
testing_level: L
---
# Feature
"""
        meta = harness_status.parse_markdown_metadata(content)
        self.assertEqual(meta.get("workflow_level"), "S")
        self.assertEqual(meta.get("testing_level"), "L")

    def test_extract_decisions(self) -> None:
        content = """
## Technical Decisions

| ID | Decision | Rationale | Assumptions |
|---|---|---|---|
| DEC-001 | Use SQLite | Faster | None |
| DEC-002 | Use pure python | YAGNI | No external libs |
"""
        decisions = harness_status.extract_decisions(content)
        self.assertEqual(len(decisions), 2)
        self.assertEqual(decisions[0]["id"], "DEC-001")
        self.assertEqual(decisions[0]["decision"], "Use SQLite")
        self.assertEqual(decisions[1]["id"], "DEC-002")

    def test_extract_assumptions(self) -> None:
        content = """
## Assumptions

- We assume python 3.10 is installed.
- No network access during tests.
"""
        assumptions = harness_status.extract_assumptions(content)
        self.assertEqual(len(assumptions), 2)
        self.assertEqual(assumptions[0], "We assume python 3.10 is installed.")
        self.assertEqual(assumptions[1], "No network access during tests.")

    def test_migrate_harness_consent_validation(self) -> None:
        valid_consent = {
            "migration_policy_accepted": True,
            "in_flight_slices_acknowledged": True
        }
        invalid_consent = {
            "migration_policy_accepted": False,
            "in_flight_slices_acknowledged": True
        }

        # Should not raise exception
        migrate_harness.validate_consent(valid_consent)

        # Should raise SystemExit
        with self.assertRaises(SystemExit):
            migrate_harness.validate_consent(invalid_consent)


    def test_scenario_a_s_level(self) -> None:
        spec_path = Path("tests/fixtures/scenario-a-s-level-crud/spec.md")
        content = spec_path.read_text(encoding="utf-8")
        meta = harness_status.parse_markdown_metadata(content)
        self.assertEqual(meta.get("workflow_level"), "S")

    def test_scenario_b_data_ml(self) -> None:
        spec_path = Path("tests/fixtures/scenario-b-data-ml/spec.md")
        content = spec_path.read_text(encoding="utf-8")
        meta = harness_status.parse_markdown_metadata(content)
        self.assertEqual(meta.get("classification"), "data_ml")

    def test_scenario_c_change_record(self) -> None:
        chg_path = Path("tests/fixtures/scenario-c-brownfield-bug/CHG-001.md")
        content = chg_path.read_text(encoding="utf-8")
        meta = harness_status.parse_markdown_metadata(content)
        self.assertEqual(meta.get("id"), "CHG-001")
        self.assertEqual(meta.get("type"), "bug")

    def test_scenario_e_consent(self) -> None:
        consent_path = Path("tests/fixtures/scenario-e-existing-migration/migration-consent.yaml")
        # Reuse migrate_harness to load consent
        # Override HARNESS_DIR temporarily
        orig_harness_dir = migrate_harness.HARNESS_DIR
        migrate_harness.HARNESS_DIR = consent_path.parent
        try:
            consent = migrate_harness.load_consent()
            self.assertEqual(consent.get("consent_id"), "CONSENT-20260717")
            self.assertEqual(consent.get("migration_policy_accepted"), True)
        finally:
            migrate_harness.HARNESS_DIR = orig_harness_dir


    def test_scenario_f_resume_without_history(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            harness_dir = root / ".harness-eng"
            harness_dir.mkdir()

            # Write a mock handover.yaml
            handover_yaml = (
                "state: building\n"
                "current_slice: F301-harness-light-policy\n"
                "workflow_level: S\n"
                "completed:\n"
                "  - task_1\n"
                "decisions:\n"
                "  - id: DEC-001\n"
                "    ref: spec.md\n"
                "assumptions:\n"
                "  - \"assume_1\"\n"
                "evidence: []\n"
                "blockers:\n"
                "  - \"blocker_1\"\n"
                "next_action: build\n"
            )
            (harness_dir / "handover.yaml").write_text(handover_yaml, encoding="utf-8")

            # Read and parse it back to simulate a fresh agent resuming
            content = (harness_dir / "handover.yaml").read_text(encoding="utf-8")

            # A simple parse logic reproducing how a fresh agent parses it
            parsed = {}
            lines = content.splitlines()
            current_key = None
            for line in lines:
                if ":" in line and not line.strip().startswith("-"):
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if v == "[]" or v == "":
                        parsed[k] = []
                    else:
                        parsed[k] = v
                elif line.strip().startswith("-"):
                    # list item
                    val = line.strip().lstrip("-").strip().strip('"').strip("'")
                    if current_key and isinstance(parsed.get(current_key), list):
                        parsed[current_key].append(val)
                # Track key context for lists
                if not line.strip().startswith("-") and ":" in line:
                    current_key = line.split(":", 1)[0].strip()

            self.assertEqual(parsed.get("state"), "building")
            self.assertEqual(parsed.get("current_slice"), "F301-harness-light-policy")
            self.assertEqual(parsed.get("workflow_level"), "S")
            self.assertEqual(parsed.get("next_action"), "build")
            self.assertIn("task_1", parsed.get("completed", []))
            self.assertIn("blocker_1", parsed.get("blockers", []))


    def test_migrate_harness_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            harness_dir = root / ".harness-eng"
            harness_dir.mkdir()

            # Setup version and slice log files
            (harness_dir / "VERSION").write_text("v0.2.6\n", encoding="utf-8")
            (harness_dir / "SLICE_LOG.md").write_text("- Initial commit\n", encoding="utf-8")

            # Mock phase active structure
            active_phase = harness_dir / "phases" / "active" / "phase-3" / "features" / "active" / "F301-harness-light-policy"
            active_phase.mkdir(parents=True)
            (active_phase / "spec.md").write_text("Mock Spec", encoding="utf-8")

            # Temporarily redirect HARNESS_DIR in migrate_harness
            orig_harness_dir = migrate_harness.HARNESS_DIR
            migrate_harness.HARNESS_DIR = harness_dir

            # Test approval flow
            os.environ["HARNESS_MIGRATION_APPROVED"] = "y"
            os.environ["HARNESS_MIGRATION_CURRENT_APPROVED"] = "n"
            try:
                migrate_harness.inspect_and_confirm_migration()

                # Check YAML was written
                migration_dir = harness_dir / "migration"
                self.assertTrue(migration_dir.is_dir())
                yamls = list(migration_dir.glob("workflow-level-*.yaml"))
                self.assertEqual(len(yamls), 1)

                # Verify Yaml content
                yaml_content = yamls[0].read_text(encoding="utf-8")
                self.assertIn("recommended_level: M", yaml_content)
                self.assertIn("approved_level: M", yaml_content)
                self.assertIn("current_slice: false", yaml_content)
                self.assertIn("future_slices: true", yaml_content)
                self.assertIn("F301-harness-light-policy", yaml_content)

                # Verify SLICE_LOG.md content
                slice_log_content = (harness_dir / "SLICE_LOG.md").read_text(encoding="utf-8")
                self.assertIn("- chore: project migrated to v0.3.0, workflow level M approved for future slices", slice_log_content)
            finally:
                os.environ.pop("HARNESS_MIGRATION_APPROVED", None)
                os.environ.pop("HARNESS_MIGRATION_CURRENT_APPROVED", None)

            # Test rejection flow
            os.environ["HARNESS_MIGRATION_APPROVED"] = "n"
            # Delete approval file to force new check
            for y in migration_dir.glob("*.yaml"):
                y.unlink()
            try:
                with self.assertRaises(SystemExit):
                    migrate_harness.inspect_and_confirm_migration()
                # Verify SLICE_LOG.md contains rejected entry
                slice_log_content = (harness_dir / "SLICE_LOG.md").read_text(encoding="utf-8")
                self.assertIn("- chore: migration recommended, not approved", slice_log_content)
            finally:
                os.environ.pop("HARNESS_MIGRATION_APPROVED", None)
                os.environ.pop("HARNESS_MIGRATION_CURRENT_APPROVED", None)
                migrate_harness.HARNESS_DIR = orig_harness_dir


    def test_migrate_harness_removes_deprecated_commands(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            harness_dir = root / ".harness-eng"
            harness_dir.mkdir()

            # Setup migration-consent.yaml
            (harness_dir / "migration-consent.yaml").write_text(
                "migration_policy_accepted: true\n"
                "in_flight_slices_acknowledged: true\n",
                encoding="utf-8"
            )

            # Mock migration decision already exists to skip interactive prompt
            migration_dir = harness_dir / "migration"
            migration_dir.mkdir()
            (migration_dir / "workflow-level-20260717.yaml").write_text("decision: approved\n", encoding="utf-8")

            # Setup commands folder
            commands_dir = harness_dir / "commands"
            commands_dir.mkdir()

            # Create a standard command file and a deprecated command file
            (commands_dir / "build.md").write_text("standard build\n", encoding="utf-8")
            (commands_dir / "health.md").write_text("deprecated health\n", encoding="utf-8")
            (commands_dir / "unknown-cmd.md").write_text("unknown command\n", encoding="utf-8")

            # Temporarily redirect HARNESS_DIR in migrate_harness
            orig_harness_dir = migrate_harness.HARNESS_DIR
            migrate_harness.HARNESS_DIR = harness_dir

            try:
                # Call apply action
                import sys as sys_orig
                orig_argv = sys_orig.argv
                sys_orig.argv = ["migrate-harness.py", "apply"]
                try:
                    migrate_harness.main()
                finally:
                    sys_orig.argv = orig_argv

                # Check build.md remains intact
                self.assertTrue((commands_dir / "build.md").is_file())

                # Check health.md and unknown-cmd.md are removed
                self.assertFalse((commands_dir / "health.md").is_file())
                self.assertFalse((commands_dir / "unknown-cmd.md").is_file())
            finally:
                migrate_harness.HARNESS_DIR = orig_harness_dir


    def test_update_spec_workflow_level(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec_file = root / "spec.md"

            # Case 1: spec has no existing workflow_level field
            spec_content = "---\ntitle: test spec\n---\nbody text\n"
            spec_file.write_text(spec_content, encoding="utf-8")

            migrate_harness.update_spec_workflow_level(spec_file, "S")
            updated = spec_file.read_text(encoding="utf-8")
            self.assertIn("workflow_level: S", updated)
            self.assertIn("title: test spec", updated)

            # Case 2: spec already has workflow_level field
            spec_content_2 = "---\ntitle: test spec\nworkflow_level: M/L\n---\nbody text\n"
            spec_file.write_text(spec_content_2, encoding="utf-8")

            migrate_harness.update_spec_workflow_level(spec_file, "M")
            updated_2 = spec_file.read_text(encoding="utf-8")
            self.assertIn("workflow_level: M", updated_2)
            self.assertNotIn("workflow_level: M/L", updated_2)


if __name__ == "__main__":
    unittest.main()
