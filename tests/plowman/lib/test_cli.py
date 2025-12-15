from unittest import mock

import pytest

from plowman.lib.cli import parse_args


@pytest.mark.parametrize(
    ("verbose", "expected_verbosity"),
    [("-v", 1), ("-vv", 2), ("-vvvvv", 5)],
)
def test_plowman_verbose(verbose: str, expected_verbosity: int) -> None:
    with mock.patch("sys.argv", ["plowman", "sow", verbose]):
        args = parse_args()

    assert args.verbosity == expected_verbosity


def test_plowman_strict() -> None:
    with mock.patch("sys.argv", ["plowman", "sow", "--dry-run"]):
        args = parse_args()
    assert args.dry_run is True
