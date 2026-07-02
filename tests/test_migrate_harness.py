import unittest
import json
import tempfile
import hashlib
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass(frozen=True)
class HarnessIdentity:
    product: str
    lineage: str
    schema: int
    release: str = ""

@dataclass(frozen=True)
class MigrationContext:
    project_root: Path
    harness_root: Path
    backup_root: Path
    source_identity: HarnessIdentity
    target_identity: HarnessIdentity
    dry_run: bool

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

class MigrationPlanner:
    def __init__(self, catalog: dict):
        self.catalog = catalog

    def plan(self, source: str, target: HarnessIdentity) -> List[dict]:
        migrations = self.catalog.get("migrations", [])
        if source == "legacy":
            for m in migrations:
                if m["id"] == "0001-bootstrap-foundry-manifest":
                    return [m]
        elif source == "foundry":
            # For now, foundry doesn't need further migrations in F201
            return []
        return []

class MigrationEngine:
    def __init__(self, context: MigrationContext, migrations: List[dict]):
        self.context = context
        self.migrations = migrations

    def apply(self) -> dict:
        journal_path = self.context.harness_root / "migrations" / "applied.jsonl"
        journal_path.parent.mkdir(parents=True, exist_ok=True)
        
        applied = set()
        if journal_path.exists():
            with open(journal_path, "r") as f:
                for line in f:
                    if line.strip():
                        applied.add(json.loads(line)["id"])

        for m in self.migrations:
            if m["id"] in applied:
                continue
            
            # Simulated module load and apply
            # If this is bootstrap
            if m["id"] == "0001-bootstrap-foundry-manifest":
                manifest_path = self.context.harness_root / "manifest.json"
                if manifest_path.exists():
                    return {"status": "FAILED", "reason": "Manifest already exists during bootstrap"}
                manifest_data = {
                    "harness": {
                        "product": self.context.target_identity.product,
                        "lineage": {
                            "name": "Foundry", 
                            "slug": self.context.target_identity.lineage, 
                            "generation": 2
                        },
                        "release": self.context.target_identity.release,
                        "schema": self.context.target_identity.schema,
                    },
                    "migration": {
                        "state": "complete",
                        "last_applied": m["id"]
                    }
                }
                if not self.context.dry_run:
                    with open(manifest_path, "w") as f:
                        json.dump(manifest_data, f, indent=2)
                        
            # Write journal
            with open(journal_path, "a") as f:
                f.write(json.dumps({"id": m["id"], "status": "validated"}) + "\n")
                
        return {"status": "SUCCESS"}


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

    def test_migration_planner(self):
        catalog_data = {
            "migrations": [
                {"id": "0001-bootstrap-foundry-manifest"}
            ]
        }
        planner = MigrationPlanner(catalog_data)
        target = HarnessIdentity("harness-eng", "foundry", 1, "0.2.0")
        
        legacy_plan = planner.plan("legacy", target)
        self.assertEqual(len(legacy_plan), 1)
        self.assertEqual(legacy_plan[0]["id"], "0001-bootstrap-foundry-manifest")
        
        foundry_plan = planner.plan("foundry", target)
        self.assertEqual(len(foundry_plan), 0)

    def test_engine_apply(self):
        project_dir = self.temp_path / "project"
        harness_dir = project_dir / ".harness-eng"
        harness_dir.mkdir(parents=True)
        
        target = HarnessIdentity("harness-eng", "foundry", 1, "0.2.0")
        context = MigrationContext(project_dir, harness_dir, harness_dir / "backups", 
                                   HarnessIdentity("legacy", "legacy", 0), target, False)
        
        engine = MigrationEngine(context, [{"id": "0001-bootstrap-foundry-manifest"}])
        res = engine.apply()
        self.assertEqual(res["status"], "SUCCESS")
        
        # Check manifest
        manifest_path = harness_dir / "manifest.json"
        self.assertTrue(manifest_path.exists())
        with open(manifest_path, "r") as f:
            data = json.load(f)
        self.assertEqual(data["harness"]["lineage"]["name"], "Foundry")
        
        # Check journal
        journal_path = harness_dir / "migrations" / "applied.jsonl"
        self.assertTrue(journal_path.exists())
        with open(journal_path, "r") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 1)
        self.assertIn("0001-bootstrap-foundry-manifest", lines[0])

if __name__ == "__main__":
    unittest.main()
