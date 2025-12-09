from pathlib import Path

from dj_settings.settings import ConfigParser

from plowman.lib.constants import CONFIG_PATH
from plowman.lib.exceptions import MissingConfigError


class BaseCommand:
    __slots__ = ("config",)

    def __init__(self) -> None:
        self.config = self._get_config()

    def _get_config(self) -> dict[Path, list[str]]:
        if not CONFIG_PATH.exists():
            raise MissingConfigError
        config = ConfigParser([CONFIG_PATH]).data["config"]
        return {Path(path): granaries for path, granaries in config.items()}

    def run(self) -> None:
        raise NotImplementedError
