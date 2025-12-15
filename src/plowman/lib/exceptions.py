from __future__ import annotations

from typing import TYPE_CHECKING

from plowman.lib.constants import CONFIG_PATH

if TYPE_CHECKING:
    from pathlib import Path


class MissingConfigError(FileNotFoundError):
    def __init__(self) -> None:
        msg = (
            "Configuration file not found. "
            f"Please create a configuration file at `{CONFIG_PATH}`."
        )
        super().__init__(msg)


class MissingGranaryError(FileNotFoundError):
    def __init__(self, granary_path: Path) -> None:
        msg = (
            f"Granary not found at path: {granary_path}. "
            "Please ensure the granary exists and is accessible."
        )
        super().__init__(msg)
