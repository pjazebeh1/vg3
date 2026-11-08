# vg3 — JSON configuration validator

A small command-line tool that checks whether a configuration file is valid JSON and, optionally, validates its contents against a JSON Schema. The schema lets you define required fields, types, allowed values, numeric limits, and other rules without changing the program.

## Requirements

- Python 3.10 or newer
- Install the dependency:

```bash
python -m pip install -r requirements.txt
```

## Usage

Check JSON syntax only:

```bash
python config_validator.py config.json
```

Validate both JSON syntax and configuration rules:

```bash
python config_validator.py config.json --schema schema.json
```

The command exits with status `0` when the file is valid, `1` when it does not match the schema, and `2` for file, JSON, schema, or dependency errors.

## Example

`config.json`:

```json
{
  "name": "demo",
  "database": {
    "host": "localhost",
    "port": 5432
  }
}
```

`schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["name", "database"],
  "properties": {
    "name": {"type": "string", "minLength": 1},
    "database": {
      "type": "object",
      "required": ["host", "port"],
      "properties": {
        "host": {"type": "string"},
        "port": {"type": "integer", "minimum": 1, "maximum": 65535}
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

Run the tests with:

```bash
python -m unittest discover -s tests
```
