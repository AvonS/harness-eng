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


blocked_state = load_module(Path("scripts/blocked-state.py"), "blocked_state")
FailureScope = blocked_state.FailureScope
clear_failure_state = blocked_state.clear_failure_state
load_failure_state = blocked_state.load_failure_state
record_failure = blocked_state.record_failure
should_block = blocked_state.should_block
write_blocked_markdown = blocked_state.write_blocked_markdown


class TestBlockedState(unittest.TestCase):
    def test_counter_and_block_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            feature_dir = root / "feature"
            feature_dir.mkdir()
            scope = FailureScope("F103", "check")
            state = None
            for _ in range(3):
                state = record_failure(scope, root, "boom")
            self.assertIsNotNone(state)
            self.assertTrue(should_block(state))
            blocked = write_blocked_markdown(feature_dir, state, "/h:build")
            self.assertTrue(blocked.is_file())
            content = blocked.read_text(encoding="utf-8")
            self.assertIn("Work item", content)
            self.assertIn("Resume command", content)
            clear_failure_state(scope, root, feature_dir)
            self.assertIsNone(load_failure_state(scope, root))
            self.assertFalse(blocked.exists())
