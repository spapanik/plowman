from __future__ import annotations

import filecmp
import shutil
from typing import TYPE_CHECKING

from plowman.commands.base import BaseCommand
from plowman.lib.constants import HOME

if TYPE_CHECKING:
    from pathlib import Path


class SowCommand(BaseCommand):
    __slots__ = ("verbosity",)

    def __init__(self, verbosity: int) -> None:
        super().__init__()
        self.verbosity = verbosity

    def sow_granary(self, granary_path: Path) -> None:
        for file in granary_path.rglob("*"):
            if file.is_dir():
                continue
            farm = HOME.joinpath(file.relative_to(granary_path)).parent
            farm.mkdir(exist_ok=True, parents=True)
            target = farm.joinpath(file.name)
            if target.exists() and filecmp.cmp(file, target, shallow=False):
                continue

            target.unlink(missing_ok=True)
            shutil.copy2(file, target)

    def run(self) -> None:
        for path, granaries in self.config.items():
            for granary in granaries:
                self.sow_granary(path.joinpath(granary))
