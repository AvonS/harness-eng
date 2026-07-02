import argparse
import sys
import json
import logging
import importlib.util
import shutil
import hashlib
import time
import uuid
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple

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
        return []

class MigrationLock:
    def __init__(self, lock_path: Path):
        self.lock_path = lock_path

    def acquire(self, run_id: str) -> bool:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.lock_path, "x") as f:
                f.write(json.dumps({"run_id": run_id, "timestamp": time.time()}))
            return True
        except FileExistsError:
            return False
            
    def release(self, run_id: str):
        try:
            with open(self.lock_path, "r") as f:
                data = json.load(f)
            if data.get("run_id") == run_id:
                self.lock_path.unlink()
        except FileNotFoundError:
            pass

class BackupManager:
    def __init__(self, backup_dir: Path):
        self.backup_dir = backup_dir
        self.manifest_path = self.backup_dir / "backup-manifest.json"
        self.manifest = []

    def backup_files(self, project_root: Path, paths: List[str]):
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        files_dir = self.backup_dir / "files"
        files_dir.mkdir(parents=True, exist_ok=True)
        
        for p in paths:
            src = project_root / p
            if src.exists():
                digest = hashlib.sha256(src.read_bytes()).hexdigest()
                size = src.stat().st_size
                dst = files_dir / str(uuid.uuid4())
                shutil.copy2(src, dst)
                self.manifest.append({
                    "original_path": p,
                    "digest": digest,
                    "size": size,
                    "backup_path": str(dst.relative_to(self.backup_dir))
                })
        
        with open(self.manifest_path, "w") as f:
            json.dump(self.manifest, f, indent=2)

class MigrationEngine:
    def __init__(self, context: MigrationContext, migrations: List[dict]):
        self.context = context
        self.migrations = migrations
        self.run_id = str(uuid.uuid4())
        self.lock = MigrationLock(self.context.harness_root / "state" / "migration.lock")
        self.backup_mgr = BackupManager(self.context.backup_root / self.run_id)

    def apply(self) -> dict:
        if not self.lock.acquire(self.run_id):
            return {"status": "LOCKED", "reason": "Another migration is running"}

        try:
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
                
                if m.get("affected_paths"):
                    self.backup_mgr.backup_files(self.context.project_root, m["affected_paths"])

                if m["id"] == "0001-bootstrap-foundry-manifest":
                    manifest_path = self.context.harness_root / "manifest.json"
                    if manifest_path.exists():
                        self.lock.release(self.run_id)
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
                        manifest_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(manifest_path, "w") as f:
                            json.dump(manifest_data, f, indent=2)
                            
                with open(journal_path, "a") as f:
                    f.write(json.dumps({"id": m["id"], "status": "validated"}) + "\n")
                    
            self.lock.release(self.run_id)
            return {"status": "SUCCESS"}
        except Exception as e:
            self.lock.release(self.run_id)
            return {"status": "FAILED", "reason": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Harness Migration Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument("--target", required=True)
    plan_parser.add_argument("--harness-dir", default=".harness-eng")
    
    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--target", required=True)
    apply_parser.add_argument("--harness-dir", default=".harness-eng")
    
    status_parser = subparsers.add_parser("status")
    
    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("--run-id", required=True)
    
    args = parser.parse_args()
    
    if args.command in ["plan", "apply"]:
        harness_root = Path(args.harness_dir)
        project_root = Path(".")
        backup_root = harness_root / "backups"
        
        source = detect_legacy_or_foundry(harness_root)
        
        target_identity = HarnessIdentity(
            product="harness-eng",
            lineage="foundry",
            schema=2,
            release="0.2.0"
        )
        
        context = MigrationContext(
            project_root=project_root,
            harness_root=harness_root,
            backup_root=backup_root,
            source_identity=HarnessIdentity("legacy", "legacy", 0),
            target_identity=target_identity,
            dry_run=(args.command == "plan")
        )
        
        catalog_path = project_root / "migrations" / "catalog.json"
        if not catalog_path.exists():
            print(json.dumps({"status": "FAILED", "reason": f"No catalog found at {catalog_path}"}))
            sys.exit(1)
            
        catalog = parse_catalog(catalog_path)
        planner = MigrationPlanner(catalog)
        plan = planner.plan(source, target_identity)
        
        if args.command == "plan":
            print(json.dumps({"status": "PLANNED", "plan": [m["id"] for m in plan]}))
            
        elif args.command == "apply":
            engine = MigrationEngine(context, plan)
            result = engine.apply()
            print(json.dumps(result))
            if result["status"] != "SUCCESS":
                sys.exit(1)
    else:
        print(f"Executing command: {args.command}")

if __name__ == "__main__":
    main()
