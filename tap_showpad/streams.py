"""Stream type classes for tap-showpad."""
from pathlib import Path

from tap_showpad.client import ShowpadStream

SCHEMA_DIR = Path(__file__).parent.joinpath("schema").resolve()


class AssetStream(ShowpadStream):
    """Asset stream."""

    name = "assets"
    path = "/exports/assets.json"
    primary_keys = ["assetId"]
    schema_filepath = SCHEMA_DIR / "assets.json"


class ChannelStream(ShowpadStream):
    """Channel stream."""

    name = "channels"
    path = "/exports/channels.json"
    primary_keys = ["channelId"]
    schema_filepath = SCHEMA_DIR / "channels.json"


class DivisionStream(ShowpadStream):
    """Division stream."""

    name = "divisions"
    path = "/exports/divisions.json"
    primary_keys = ["divisionId"]
    schema_filepath = SCHEMA_DIR / "divisions.json"


class ContactStream(ShowpadStream):
    """Contact stream."""

    name = "contacts"
    path = "/exports/contacts.json"
    primary_keys = ["contactId"]
    schema_filepath = SCHEMA_DIR / "contacts.json"


class UserStream(ShowpadStream):
    """User stream."""

    name = "users"
    path = "/exports/users.json"
    primary_keys = ["userId"]
    schema_filepath = SCHEMA_DIR / "users.json"


class SharedSpaceStream(ShowpadStream):
    """Shared space stream."""

    name = "sharedspaces"
    path = "/exports/sharedspaces.json"
    primary_keys = ["sharedSpaceId"]
    schema_filepath = SCHEMA_DIR / "sharedspaces.json"


class SharedSpaceParticipantStream(ShowpadStream):
    """Shared space participant stream."""

    name = "sharedspaceparticipants"
    path = "/exports/sharedspaceparticipants.json"
    primary_keys = ["sharedSpaceParticipantId"]
    schema_filepath = SCHEMA_DIR / "sharedspaceparticipants.json"
