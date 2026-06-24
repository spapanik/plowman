from unittest import mock

from plowman.__main__ import main


def test_main_exit_case() -> None:
    """Test subcommand doesn't match any known command (implicit exit)."""
    with mock.patch(
        "plowman.__main__.parse_args",
        new=mock.MagicMock(
            return_value=mock.MagicMock(verbosity=0, subcommand=None, dry_run=False)
        ),
    ):
        main()
