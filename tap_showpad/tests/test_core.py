"""Tests standard tap features using the built-in SDK tests library."""
import os

from singer_sdk.testing import get_standard_tap_tests, tap_sync_test
from tap_showpad.tap import TapShowpad

BASE_CONFIG = {
    "subdomain": os.getenv("SHOWPAD_SUBDOMAIN"),
    "api_key": os.getenv("SHOWPAD_API_KEY"),
    "user_agent": "tap-showpad",
}


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(TapShowpad, config=BASE_CONFIG)
    for test in tests:
        test()


def test_run():
    """Run standard tap tests from the SDK."""
    tap_sync_test(TapShowpad(config=BASE_CONFIG))


if __name__ == "__main__":
    test_run()
