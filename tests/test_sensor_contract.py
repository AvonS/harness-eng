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


sensor_runner = load_module(Path("scripts/sensor-runner.py"), "sensor_runner")
Sensor = sensor_runner.Sensor
SensorConfigurationError = sensor_runner.SensorConfigurationError
SensorExecutionError = sensor_runner.SensorExecutionError
load_sensors = sensor_runner.load_sensors
render_sensor_table = sensor_runner.render_sensor_table
run_sensor = sensor_runner.run_sensor
run_sensors_for_hook = sensor_runner.run_sensors_for_hook
select_sensors = sensor_runner.select_sensors


class TestSensorContract(unittest.TestCase):
    def test_load_select_and_render(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = root / "technology.yaml"
            config.write_text(
                "- id: unit-tests\n  command: python3 -c 'print(1)'\n  required_before: verify\n  timeout: 5\n  evidence: logs\n",
                encoding="utf-8",
            )
            sensors = load_sensors(config)
            self.assertEqual(len(sensors), 1)
            selected = select_sensors(sensors, "verify")
            self.assertEqual(len(selected), 1)
            evidence_root = root / "evidence"
            result = run_sensor(selected[0], root, evidence_root)
            self.assertTrue(result.evidence_path.is_file())
            self.assertIn("unit-tests", render_sensor_table([result]))

    def test_fail_closed_on_failure_and_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence_root = root / "evidence"
            failing = Sensor("fail", "python3 -c 'import sys; sys.exit(1)'", ["verify"], 1, "logs")
            with self.assertRaises(SensorExecutionError):
                run_sensor(failing, root, evidence_root)
            missing = Sensor("missing", "missing-command-zzzz", ["verify"], 1, "logs")
            with self.assertRaises(SensorExecutionError):
                run_sensor(missing, root, evidence_root)
            timeout = Sensor("timeout", "python3 -c 'import time; time.sleep(2)'", ["verify"], 1, "logs")
            with self.assertRaises(SensorExecutionError):
                run_sensor(timeout, root, evidence_root)

    def test_required_hook_without_sensor_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            config = root / "technology.yaml"
            config.write_text(
                "- id: unit-tests\n  command: python3 -c 'print(1)'\n  required_before: release\n  timeout: 5\n  evidence: logs\n",
                encoding="utf-8",
            )
            with self.assertRaises(SensorConfigurationError):
                run_sensors_for_hook(config, "verify", root, root / "evidence")
