"""Showpad tap class."""
import json
from pathlib import Path
from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th

from tap_showpad.streams import (
    ShowpadStream,
    SharedSpaceStream,
    SharedSpaceParticipantStream,
    UserStream,
    ContactStream,
    DivisionStream,
    ChannelStream,
    AssetStream,
)

STREAM_TYPES = [
    SharedSpaceStream,
    SharedSpaceParticipantStream,
    UserStream,
    ContactStream,
    DivisionStream,
    ChannelStream,
    AssetStream,
]


class TapShowpad(Tap):
    """Showpad tap class."""

    name = "tap-showpad"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "subdomain",
            th.StringType,
            required=True,
            description="The subdomain of your Showpad instance",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_type(tap=self) for stream_type in STREAM_TYPES]

    def _discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams from the openapi schema."""
        schema_path = Path(__file__).parent / "schema" / "openapi.json"
        schema = json.loads(schema_path.read_text())
        for path, methods in schema["paths"].items():
            # Only GET endpoints
            if "get" not in methods:
                continue
            spec = methods["get"]
            # No parameterized paths
            # An actual implementation should use a
            # developer-defined whitelist of endpoints
            if any(fstring in path for fstring in ["{", "}"]):
                continue
            # Name the stream after the operationId
            if "operationId" in spec:
                op = spec["operationId"]
            elif "operation_id" in spec:
                op = spec["operation_id"]
            else:
                continue
            # We expect a response object with a list of items
            jsonresp = spec["responses"]["default"]["content"]["application/json"]
            jsonschema = jsonresp["schema"]
            if "response" not in jsonschema.get("required", []):
                continue
            # Resp should have `count` and `items`
            resp_jsonschema = jsonschema["properties"]["response"]
            if "items" not in resp_jsonschema["properties"]:
                continue
            # properties.items should be an array
            items_jsonschema = resp_jsonschema["properties"]["items"]["items"]
            # Dynamically create a stream class for each endpoint
            yield type(
                op,
                (ShowpadStream,),
                {
                    "name": op[4:],
                    "path": path,
                    "primary_keys": ["id"],
                    "api_version": "v3",
                    "records_jsonpath": "$.response.items[*]",
                    "schema": items_jsonschema,
                },
            )(tap=self)


if __name__ == "__main__":
    TapShowpad.cli()
