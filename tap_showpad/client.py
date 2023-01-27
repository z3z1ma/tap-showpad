"""REST client handling, including ShowpadStream base class."""
import datetime
import os
from typing import Any, Dict, Iterable, Optional

import requests
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.helpers._state import (
    PROGRESS_MARKER_NOTE,
    PROGRESS_MARKERS,
    InvalidStreamSortException,
    to_json_compatible,
)
from singer_sdk.helpers._typing import TypeConformanceLevel
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator, BaseOffsetPaginator
from singer_sdk.streams import RESTStream
from singer_sdk.streams.core import (  # noqa: F401
    REPLICATION_FULL_TABLE,
    REPLICATION_INCREMENTAL,
)

PAGE_SIZE = 50000


class ShowpadPaginator(BaseOffsetPaginator):
    def __init__(
        self, start_value: int, page_size: int, api: str, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(start_value, page_size, *args, **kwargs)
        self.max_ts = datetime.datetime(1970, 1, 1)
        self.api = api

    def has_more(self, response: requests.Response) -> bool:
        """Return True if the response has more data to be retrieved."""
        if self.api == "v4":
            # No fancy logic for v4, just check if we got the full page
            return len(response.json()["items"]) >= self._page_size
        # Assume v3
        r = response.json()["response"]
        if r["count"] == 0 or len(r["items"]) == 0:
            return False
        try:
            ts = max(
                datetime.datetime.strptime(t["createdAt"], "%Y-%m-%dT%H:%M:%S.%fZ")
                for t in r["items"]
            )
            if ts > self.max_ts:
                self.max_ts = ts
                return True
            return False
        except KeyError:
            # A safe fallback for streams that don't have a createdAt field
            return r["count"] >= self._page_size


class ShowpadStream(RESTStream):
    """Showpad stream class."""

    api_version = "v3"
    # We don't need the SDK to check this for us
    is_sorted = False
    check_sorted = False

    TYPE_CONFORMANCE_LEVEL = TypeConformanceLevel.NONE

    if "SDK_DEBUG_RECORD_LIMIT" in os.environ:
        _MAX_RECORDS_LIMIT = int(os.environ["SDK_DEBUG_RECORD_LIMIT"])

    @property
    def records_jsonpath(self):
        if self.api_version == "v3":
            return "$.response.items[*]"
        elif self.api_version == "v4":
            return "$.items[*]"
        else:
            raise ValueError("Unknown API version")

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        if self.api_version == "v3":
            return "https://{}.showpad.biz/api/v3".format(self.config["subdomain"])
        elif self.api_version == "v4":
            return "https://{}.api.showpad.com/v4".format(self.config["subdomain"])
        else:
            raise ValueError("Unknown API version")

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object.

        This method is called by the SDK framework to get an authenticator."""
        return BearerTokenAuthenticator.create_for_stream(self, token=self.config["api_key"])

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        This method is called by the SDK framework to get the headers."""
        headers = {"User-Agent": self.config.get("user_agent", "tap-showpad")}
        return headers

    def get_new_paginator(self) -> BaseAPIPaginator:
        return ShowpadPaginator(
            start_value=0,
            page_size=PAGE_SIZE,
            api=self.api_version,
        )

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["offset"] = next_page_token
        params["limit"] = PAGE_SIZE
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records."""
        for record in extract_jsonpath(self.records_jsonpath, input=response.json()):
            # We can pre-process the record here if needed
            yield record
