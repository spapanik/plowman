from unittest import mock

from plowman.__main__ import main


@mock.patch(
    "plowman.__main__.parse_args",
    new=mock.MagicMock(
        return_value=mock.MagicMock(verbosity=3, subcommand="sow", dry_run=False)
    ),
)
@mock.patch("plowman.__main__.SowCommand")
def test_clone(mock_command: mock.MagicMock) -> None:
    main()
    assert mock_command.call_count == 1
    calls = [mock.call(dry_run=False, verbosity=3)]
    assert mock_command.call_args_list == calls
