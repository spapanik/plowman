from plowman.lib.constants import CONFIG_PATH


class MissingConfigError(FileNotFoundError):
    def __init__(self) -> None:
        msg = (
            "Configuration file not found. "
            f"Please create a configuration file at `{CONFIG_PATH}`."
        )
        super().__init__(msg)
