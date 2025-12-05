from plowman.commands.base import BaseCommand


class SowCommand(BaseCommand):
    __slots__ = ("verbosity",)

    def __init__(self, verbosity: int) -> None:
        super().__init__()
        self.verbosity = verbosity
