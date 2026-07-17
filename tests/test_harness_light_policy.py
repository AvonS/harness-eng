import importlib.util
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


if __name__ == "__main__":
    unittest.main()
