from pathlib import Path

import pytest

from plowman.lib.exceptions import MissingConfigError, MissingGranaryError


def test_missing_config_error() -> None:
    with pytest.raises(MissingConfigError) as exc_info:
        raise MissingConfigError
    assert "Configuration file not found" in str(exc_info.value)


def test_missing_granary_error(tmp_path: Path) -> None:
    granary_path = tmp_path / "nonexistent_granary"
    with pytest.raises(MissingGranaryError) as exc_info:
        raise MissingGranaryError(granary_path)
    assert str(granary_path) in str(exc_info.value)
    assert "Granary not found" in str(exc_info.value)
