"""Infers schemas from a tap's output.

Usage:
    tap-<whatever> | python schema_inferrer.py
    tap-<whatever> | head -500 | python schema_inferrer.py
"""

import json
import sys

import genson

if __name__ == "__main__":
    schemas: dict[str, genson.Schema] = {}
    schema = genson.Schema()
    for line in sys.stdin:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        if message["type"] == "RECORD":
            if message["stream"] not in schemas:
                schemas[message["stream"]] = genson.Schema()
            schemas[message["stream"]].add_object(message["record"])
    for stream, schema in schemas.items():
        print(stream)
        print(schema.to_json(indent=2))
        print()
