import importlib.util
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


traceability = load_module(Path("scripts/traceability.py"), "traceability")
parse_scenarios = traceability.parse_scenarios
parse_task_links = traceability.parse_task_links
render_traceability_table = traceability.render_traceability_table
validate_traceability = traceability.validate_traceability


class TestTraceabilityContract(unittest.TestCase):
    def test_parse_and_render(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec = root / "spec.md"
            spec.write_text(
                """```yaml
scenario_id: SCN-001
source_requirement: docs/backlog.md#x
provenance: Confirmed
given: g
when: w
then: t
evidence_strategy: tests/test_traceability_contract.py
```
""",
                encoding="utf-8",
            )
            tasks = root / "tasks.md"
            tasks.write_text("- [x] [US1] SCN-001 task\n", encoding="utf-8")
            evidence = root / "tests" / "evidence.txt"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("SCN-001", encoding="utf-8")
            scenarios = parse_scenarios(spec)
            self.assertEqual([s.scenario_id for s in scenarios], ["SCN-001"])
            links = parse_task_links(tasks)
            coverage = validate_traceability(scenarios, links, root)
            self.assertEqual(coverage[0].status, "PASS")
            self.assertEqual(coverage[0].evidence_paths, [evidence])
            table = render_traceability_table(coverage)
            self.assertIn("SCN-001", table)

    def test_review_pre_verify_allows_missing_evidence_but_requires_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            spec = root / "spec.md"
            spec.write_text(
                """```yaml
scenario_id: SCN-002
source_requirement: docs/backlog.md#y
provenance: Confirmed
given: g
when: w
then: t
evidence_strategy: verification.md
```
""",
                encoding="utf-8",
            )
            tasks = root / "tasks.md"
            tasks.write_text("- [x] SCN-002 task\n", encoding="utf-8")
            coverage = validate_traceability(parse_scenarios(spec), parse_task_links(tasks), root, require_evidence=False)
            self.assertEqual(coverage[0].status, "PASS")
