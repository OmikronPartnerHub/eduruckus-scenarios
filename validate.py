#!/usr/bin/env python3
"""
Validate scenarios against scenarios.schema.yml.
Requires jsonschema and PyYAML. Run with: python3 validate.py
"""

from pathlib import Path
import sys
import jsonschema
import yaml


def load_yaml(path):
    """Read a single YAML document without constructing arbitrary objects."""
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def main():
    """Main function"""
    root = Path(__file__).resolve().parent
    schema_path = root / "scenarios.schema.yml"
    try:
        schema = load_yaml(schema_path)
        validator_class = jsonschema.validators.validator_for(schema)
        validator_class.check_schema(schema)
        validator = validator_class(schema)
    except (OSError, UnicodeError, yaml.YAMLError, jsonschema.SchemaError) as error:
        print(f"Cannot load schema {schema_path}: {error}", file=sys.stderr)
        return 1

    scenarios_dir = root / "scenarios"
    files = sorted(
        path
        for path in scenarios_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
    )
    if not files:
        print(f"No YAML scenario files found in {scenarios_dir}", file=sys.stderr)
        return 1

    failed = 0
    for path in files:
        name = path.relative_to(root)
        try:
            scenario = load_yaml(path)
        except (OSError, UnicodeError, yaml.YAMLError) as error:
            print(f"FAIL {name}: {error}", file=sys.stderr)
            failed += 1
            continue

        errors = sorted(
            validator.iter_errors(scenario),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        if errors:
            failed += 1
            for error in errors:
                location = "$" + "".join(
                    f"[{part!r}]" for part in error.absolute_path
                )
                print(f"FAIL {name} {location}: {error.message}", file=sys.stderr)
        else:
            print(f"PASS {name}")

    print(f"Validated {len(files)} file(s): {len(files) - failed} passed, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
