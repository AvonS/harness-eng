import json
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class MigrationContext:
    project_root: Path
    harness_root: Path
    backup_root: Path
    source_identity: dict
    target_identity: dict
    dry_run: bool

class Migration:
    def inspect(self, context: MigrationContext) -> dict:
        manifest_path = context.harness_root / "manifest.json"
        if manifest_path.exists():
            return {"status": "ALREADY_APPLIED"}
        return {"status": "NEEDS_APPLY"}

    def apply(self, context: MigrationContext) -> dict:
        manifest_path = context.harness_root / "manifest.json"
        
        manifest_data = {
            "harness": {
                "product": context.target_identity.get("product", "harness-eng"),
                "lineage": {
                    "name": "Foundry", 
                    "slug": "foundry", 
                    "generation": 2
                },
                "release": context.target_identity.get("release", "0.2.0"),
                "schema": 1,
            },
            "migration": {
                "state": "complete",
                "last_applied": "0001-bootstrap-foundry-manifest"
            }
        }
        
        if not context.dry_run:
            with open(manifest_path, "w") as f:
                json.dump(manifest_data, f, indent=2)
                
        return {"status": "SUCCESS"}

    def validate(self, context: MigrationContext) -> dict:
        manifest_path = context.harness_root / "manifest.json"
        if not manifest_path.exists():
            return {"status": "FAILED", "reason": "manifest.json missing"}
        with open(manifest_path, "r") as f:
            data = json.load(f)
        if data.get("harness", {}).get("lineage", {}).get("name") != "Foundry":
            return {"status": "FAILED", "reason": "lineage is not Foundry"}
        return {"status": "SUCCESS"}
