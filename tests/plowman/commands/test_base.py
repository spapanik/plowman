from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock

import pytest

from plowman.commands.base import BaseCommand
from plowman.lib.exceptions import MissingConfigError, MissingGranaryError

if TYPE_CHECKING:
    from plowman.lib.type_defs import PlowmanConfig


def test_base_command_missing_config() -> None:
    with (
        mock.patch(
            "plowman.commands.base.CONFIG_PATH", Path("/nonexistent/config.yml")
        ),
        pytest.raises(MissingConfigError),
    ):
        BaseCommand()


def test_base_command_parse_config_missing_granary(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    config_path.write_text(f"estates:\n  {tmp_path}:\n    granaries: []\n")

    with mock.patch("plowman.commands.base.CONFIG_PATH", config_path):
        cmd = BaseCommand()

    path = tmp_path / "test_path"
    path.mkdir()
    config: PlowmanConfig = {
        "granaries": ["missing_granary"],
    }

    with pytest.raises(MissingGranaryError):
        list(cmd._parse_config(path, config))


def test_base_command_parse_config_success(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    granary_dir = tmp_path / "my_granary"
    granary_dir.mkdir()

    config_path.write_text(f"estates:\n  {tmp_path}:\n    granaries: [my_granary]\n")

    with mock.patch("plowman.commands.base.CONFIG_PATH", config_path):
        cmd = BaseCommand()

    config: PlowmanConfig = {"granaries": ["my_granary"], "variables": {"key": "value"}}
    result = list(cmd._parse_config(tmp_path, config))

    assert len(result) == 1
    assert result[0]["granary"] == granary_dir
    assert result[0]["variables"] == {"key": "value"}


def test_base_command_run_not_implemented(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yml"
    granary_dir = tmp_path / "my_granary"
    granary_dir.mkdir()
    config_path.write_text(f"estates:\n  {tmp_path}:\n    granaries: [my_granary]\n")
    with (
        mock.patch("plowman.commands.base.CONFIG_PATH", config_path),
        pytest.raises(NotImplementedError),
    ):
        BaseCommand().run()
