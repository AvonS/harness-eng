import unittest
import json
import tempfile
import hashlib
from pathlib import Path

def parse_catalog(catalog_path: Path) -> dict:
    with open(catalog_path, "r") as f:
        return json.load(f)

def detect_legacy_or_foundry(harness_dir: Path) -> str:
    if not harness_dir.exists():
        return "not_initialized"
    manifest_path = harness_dir / "manifest.json"
    if not manifest_path.exists():
        return "legacy"
    try:
        with open(manifest_path, "r") as f:
            data = json.load(f)
        lineage_name = data.get("harness", {}).get("lineage", {}).get("name")
        if lineage_name == "Foundry":
            return "foundry"
    except Exception:
        pass
    return "legacy"

class TestMigrateHarness(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_catalog_parsing(self):
        catalog_path = self.temp_path / "catalog.json"
        catalog_data = {
            "catalog_version": 1,
            "target": {"product": "harness-eng", "lineage": "foundry", "release": "0.2.0", "schema": 2},
            "supported_sources": ["legacy-v1", "foundry"],
            "migrations": [
                {
                    "id": "0001-bootstrap-foundry-manifest",
                    "phase": "pre_upgrade",
                    "from": {"lineage": "foundry", "schema": 0},
                    "to": {"lineage": "foundry", "schema": 1},
                    "module": "0001-bootstrap-foundry-manifest.py",
                    "sha256": "fake_digest",
                    "affected_paths": [".harness-eng/manifest.json"]
                }
            ]
        }
        with open(catalog_path, "w") as f:
            json.dump(catalog_data, f)
            
        parsed = parse_catalog(catalog_path)
        self.assertEqual(parsed["catalog_version"], 1)
        self.assertEqual(parsed["target"]["lineage"], "foundry")
        self.assertEqual(len(parsed["migrations"]), 1)

    def test_legacy_fingerprint_detection(self):
        legacy_dir = self.temp_path / "legacy_project" / ".harness-eng"
        legacy_dir.mkdir(parents=True)
        self.assertEqual(detect_legacy_or_foundry(legacy_dir), "legacy")
        
        foundry_dir = self.temp_path / "foundry_project" / ".harness-eng"
        foundry_dir.mkdir(parents=True)
        manifest_path = foundry_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump({"harness": {"lineage": {"name": "Foundry"}}}, f)
            
        self.assertEqual(detect_legacy_or_foundry(foundry_dir), "foundry")
        
        empty_project_dir = self.temp_path / "empty_project" / ".harness-eng"
        self.assertEqual(detect_legacy_or_foundry(empty_project_dir), "not_initialized")

if __name__ == "__main__":
    unittest.main()
