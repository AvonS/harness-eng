import importlib.util, json, os, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module); return module

delegation = load(ROOT / "scripts/validate-delegation-contracts.py", "delegation")
layout = load(ROOT / "scripts/harness_layout.py", "layout")
migration = load(ROOT / "migrations/0002-phase-level-lifecycle.py", "phase_migration")

class Contracts(unittest.TestCase):
    def test_delegation_contracts(self):
        self.assertEqual(delegation.validate(ROOT / "commands"), [])

    def test_reviews_are_read_only_and_skill_aware(self):
        for name in ("review-pre-build.md", "review-pre-verify.md"):
            text = (ROOT / "commands" / name).read_text()
            for expected in ("capability: review", "write_authority: none", "Skill Evidence", "load_relevant_skills"):
                self.assertIn(expected, text)

    def test_layout_manifest(self):
        manifest = json.loads((ROOT / "templates/init-layout.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for item in manifest["required_directories"]: (root / item).mkdir(parents=True, exist_ok=True)
            for item in manifest["required_files"]:
                path = root / item; path.parent.mkdir(parents=True, exist_ok=True); path.write_text("x")
            for item, target in manifest["required_symlinks"].items(): os.symlink(target, root / item)
            self.assertEqual(layout.validate_layout(root, manifest), [])
            (root / ".harness-eng/sanity-check.sh").write_text("bad")
            self.assertIn("misplaced path: .harness-eng/sanity-check.sh", layout.validate_layout(root, manifest))

    def test_phase_discovery_and_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = Path(tmp) / ".harness-eng"; old = harness / "phases/phase-0/features"
            (old / "active/F002").mkdir(parents=True); (old / "done/F001").mkdir(parents=True)
            migration.migrate_phase_layout(harness)
            feature = harness / "phases/active/phase-0/features"
            self.assertTrue((feature / "F001").is_dir() and (feature / "F002").is_dir())
            (feature / "F002/spec.md").write_text("spec")
            self.assertEqual(layout.active_artifacts(harness, "spec.md"), [feature / "F002/spec.md"])
            self.assertEqual(migration.migrate_phase_layout(harness), [])

    def test_migration_collision_is_preflighted(self):
        with tempfile.TemporaryDirectory() as tmp:
            harness = Path(tmp) / ".harness-eng"; phases = harness / "phases"
            (phases / "phase-0/features/active/F001").mkdir(parents=True)
            (phases / "phase-1/features/active/F002").mkdir(parents=True)
            (phases / "active/phase-1").mkdir(parents=True)
            with self.assertRaises(FileExistsError): migration.migrate_phase_layout(harness)
            self.assertTrue((phases / "phase-0/features/active/F001").is_dir())

    def test_small_requires_runtime_smoke(self):
        text = (ROOT / "commands/init.md").read_text()
        self.assertIn("derive_runtime_smoke", text); self.assertIn("real-entry-point", text)

if __name__ == "__main__": unittest.main()
