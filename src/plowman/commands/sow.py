from __future__ import annotations

import filecmp
import shutil
from typing import TYPE_CHECKING

from pyutilkit.term import SGRString

from plowman.commands.base import BaseCommand
from plowman.lib.constants import HOME

if TYPE_CHECKING:
    from pathlib import Path


class SowCommand(BaseCommand):
    __slots__ = ("dry_run", "verbosity")

    def __init__(self, verbosity: int, *, dry_run: bool) -> None:
        super().__init__()
        self.verbosity = verbosity
        self.dry_run = dry_run

    def _get_crop_path(self, granary: Path, seed: Path) -> Path:
        farm = HOME.joinpath(seed.relative_to(granary)).parent
        farm.mkdir(exist_ok=True, parents=True)
        return farm.joinpath(seed.name)

    def _should_skip(self, seed: Path, crop: Path) -> bool:
        if not crop.exists():
            return False
        return filecmp.cmp(seed, crop, shallow=False)

    def _plant_crop(self, seed: Path, crop: Path) -> None:
        crop.unlink(missing_ok=True)
        shutil.copy2(seed, crop)

    def sow_granary(self, granary_path: Path) -> None:
        for seed in granary_path.rglob("*"):
            if seed.is_dir():
                continue
            crop = self._get_crop_path(granary_path, seed)
            if self._should_skip(seed, crop):
                continue
            if self.dry_run:
                SGRString(f"Would copy {seed} to {crop}", prefix="☑️ ").print()
                continue

            self._plant_crop(seed, crop)

    def run(self) -> None:
        for path, granaries in self.config.items():
            for granary in granaries:
                self.sow_granary(path.joinpath(granary))
