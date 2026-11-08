import json
import tempfile
import unittest
from pathlib import Path

from config_validator import load_json, validate


class ConfigValidatorTests(unittest.TestCase):
    def test_valid_config_passes_schema(self):
        schema = {
            "type": "object",
            "required": ["name", "port"],
            "properties": {
                "name": {"type": "string"},
                "port": {"type": "integer", "minimum": 1, "maximum": 65535},
            },
            "additionalProperties": False,
        }
        self.assertEqual(validate({"name": "demo", "port": 8080}, schema), [])

    def test_invalid_config_reports_missing_and_wrong_types(self):
        schema = {
            "type": "object",
            "required": ["name", "port"],
            "properties": {"name": {"type": "string"}, "port": {"type": "integer"}},
        }
        errors = validate({"name": 42}, schema)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("port" in error and "required" in error for error in errors))
        self.assertTrue(any("name" in error and "string" in error for error in errors))

    def test_load_json_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps({"enabled": True}), encoding="utf-8")
            self.assertEqual(load_json(path), {"enabled": True})

    def test_invalid_json_has_location(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.json"
            path.write_text('{"missing": }', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"broken\.json:1:"):
                load_json(path)


if __name__ == "__main__":
    unittest.main()
