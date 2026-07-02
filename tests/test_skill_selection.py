import importlib.util
import json
import sys
import tempfile
from pathlib import Path
import unittest


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


skill_selection = load_module(Path("scripts/skill-selection.py"), "skill_selection")
SkillMatch = skill_selection.SkillMatch
detect_technology = skill_selection.detect_technology
install_skills = skill_selection.install_skills
offline_failure_message = skill_selection.offline_failure_message
main = skill_selection.main
preserve_project_modifications = skill_selection.preserve_project_modifications
render_preview = skill_selection.render_preview
resolve_skills = skill_selection.resolve_skills
write_install_log = skill_selection.write_install_log


class TestSkillSelection(unittest.TestCase):
    def test_resolve_and_preview(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "skills" / "python").mkdir(parents=True)
            (root / "skills" / "python" / "SKILL.md").write_text("name: python", encoding="utf-8")
            (root / "skills" / "git").mkdir(parents=True)
            (root / "skills" / "git" / "SKILL.md").write_text("name: git", encoding="utf-8")
            (root / "technology.yaml").write_text("skills: [python, git]", encoding="utf-8")
            tech = detect_technology(root)
            self.assertEqual(tech, ["git", "python"])
            matches = resolve_skills(tech, root)
            self.assertEqual([m.name for m in matches], ["git", "python"])
            preview = render_preview(matches)
            self.assertIn("Selected skills preview:", preview)
            self.assertIn("git", preview)
            self.assertIn("python", preview)

    def test_install_log_and_preservation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            src = root / "skills" / "python"
            src.mkdir(parents=True)
            (src / "SKILL.md").write_text("name: python\nversion: 1\n", encoding="utf-8")
            matches = [SkillMatch("python", str(src), "1", src)]
            dest = root / ".harness-eng" / "skills"
            log_path = root / ".harness-eng" / "skill-install.json"
            records = install_skills(matches, dest, log_path)
            write_install_log(records, log_path)

            installed = dest / "python" / "SKILL.md"
            self.assertIn("version: 1", installed.read_text(encoding="utf-8"))

            (src / "SKILL.md").write_text("name: python\nversion: 2\n", encoding="utf-8")
            matches = [SkillMatch("python", str(src), "2", src)]
            records = install_skills(matches, dest, log_path)
            write_install_log(records, log_path)
            self.assertEqual(records[0].action, "installed")
            self.assertIn("version: 2", installed.read_text(encoding="utf-8"))

            installed.write_text("name: python\nversion: 2\ncustom: kept\n", encoding="utf-8")
            (src / "SKILL.md").write_text("name: python\nversion: 3\n", encoding="utf-8")
            matches = [SkillMatch("python", str(src), "3", src)]
            records = install_skills(matches, dest, log_path)
            write_install_log(records, log_path)
            self.assertEqual(records[0].action, "preserved")
            self.assertIn("custom: kept", installed.read_text(encoding="utf-8"))
            preserved = preserve_project_modifications(dest, log_path)
            self.assertEqual(preserved, [installed])

            payload = json.loads(log_path.read_text(encoding="utf-8"))
            self.assertEqual(payload[0]["name"], "python")

    def test_offline_failure_message(self) -> None:
        self.assertIn("harness-eng-skills clone or local cache", offline_failure_message())

    def test_cli_preview_only(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "skills" / "python").mkdir(parents=True)
            (root / "skills" / "python" / "SKILL.md").write_text("name: python", encoding="utf-8")
            (root / "technology.yaml").write_text("skills: [python]", encoding="utf-8")
            rc = main(["--root", str(root), "--preview-only"])
            self.assertEqual(rc, 0)

    def test_explicit_external_source_root(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "project"
            source = Path(td) / "harness-eng-skills" / "skills"
            root.mkdir()
            (source / "python").mkdir(parents=True)
            (source / "python" / "SKILL.md").write_text("name: python", encoding="utf-8")
            (root / "technology.yaml").write_text("skills: [python]", encoding="utf-8")

            rc = main(["--root", str(root), "--source-root", str(source), "--preview-only"])

            self.assertEqual(rc, 0)
