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


def test_main_harvest_case() -> None:
    """Test harvest subcommand is dispatched correctly."""
    mock_command = mock.MagicMock()
    with (
        mock.patch(
            "plowman.__main__.parse_args",
            new=mock.MagicMock(
                return_value=mock.MagicMock(
                    verbosity=0, subcommand="harvest", dry_run=False, add_to_estate=[]
                )
            ),
        ),
        mock.patch("plowman.__main__.HarvestCommand", return_value=mock_command),
    ):
        main()
        mock_command.run.assert_called_once()
