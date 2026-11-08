#!/usr/bin/env python3
"""Validate JSON configuration files, optionally against a JSON Schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    """Load JSON from a file and provide useful errors to the CLI caller."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path}: file is not valid UTF-8 ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{path}:{exc.lineno}:{exc.colno}: invalid JSON: {exc.msg}"
        ) from exc
    except OSError as exc:
        raise ValueError(f"{path}: cannot read file: {exc.strerror or exc}") from exc


def validate(config: Any, schema: Any) -> list[str]:
    """Return validation errors for config against the provided JSON Schema."""
    try:
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError
    except ImportError as exc:
        raise RuntimeError(
            "JSON Schema validation requires the 'jsonschema' package. "
            "Install dependencies with: python -m pip install -r requirements.txt"
        ) from exc

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        location = ".".join(str(part) for part in exc.absolute_path) or "<schema>"
        return [f"Invalid schema at {location}: {exc.message}"]

    validator = Draft202012Validator(schema)
    errors = []
    for error in sorted(
        validator.iter_errors(config),
        key=lambda item: (list(map(str, item.absolute_path)), item.message),
    ):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{location}: {error.message}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check a JSON configuration file, optionally against a JSON Schema."
    )
    parser.add_argument("config", type=Path, help="path to the JSON configuration file")
    parser.add_argument(
        "--schema", type=Path, help="path to a JSON Schema (Draft 2020-12) file"
    )
    args = parser.parse_args(argv)

    try:
        config = load_json(args.config)
        if args.schema is None:
            print(f"Valid JSON: {args.config}")
            print("No schema supplied; structural rules were not checked.")
            return 0

        schema = load_json(args.schema)
        errors = validate(config, schema)
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if errors:
        print(f"Configuration is invalid ({len(errors)} issue(s)):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Configuration is valid: {args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
