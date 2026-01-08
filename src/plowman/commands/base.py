from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from dj_settings.settings import ConfigParser

from plowman.lib.constants import CONFIG_PATH
from plowman.lib.exceptions import MissingConfigError, MissingGranaryError

if TYPE_CHECKING:
    from collections.abc import Iterator

    from plowman.lib.type_defs import ParsedConfig, PlowmanConfig


class BaseCommand:
    __slots__ = ("allow_symlinks", "config", "granary_config")

    def __init__(self) -> None:
        self.config = self._get_config()
        self.allow_symlinks = ConfigParser([CONFIG_PATH]).data.get(
            "allow_symlinks", False
        )

    def _parse_config(
        self, path: Path, config: PlowmanConfig
    ) -> Iterator[ParsedConfig]:
        variables = config.get("variables", {})
        path_config = path.joinpath(".plowman", "plowman.yml")
        estate = path.joinpath(".plowman", "estate.yml")
        data = ConfigParser([path_config]).data if path_config.exists() else {}
        for granary_name in config.get("granaries", []):
            granary_path = path.joinpath(granary_name)
            if not granary_path.exists() or not granary_path.is_dir():
                raise MissingGranaryError(granary_path)
            templates = data.get(granary_name, {}).get("templates", [])
            yield {
                "estate": estate,
                "variables": variables,
                "granary": granary_path,
                "templates": {
                    granary_path.joinpath(template) for template in templates
                },
            }

    def _get_config(self) -> list[ParsedConfig]:
        if not CONFIG_PATH.exists():
            raise MissingConfigError
        config_path = ConfigParser([CONFIG_PATH]).data["granaries"]
        return [
            granary_config
            for path, config in config_path.items()
            for granary_config in self._parse_config(Path(path), config)
        ]

    def run(self) -> None:
        raise NotImplementedError
