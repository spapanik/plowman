from __future__ import annotations

from hashlib import sha256
from typing import TYPE_CHECKING

from jinja2 import StrictUndefined, Template
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

    def _get_crop_path(self, granary: Path, seed: Path, *, is_template: bool) -> Path:
        farm = HOME.joinpath(seed.relative_to(granary)).parent
        farm.mkdir(exist_ok=True, parents=True)
        seed_name = seed.with_suffix("").name if is_template else seed.name
        return farm.joinpath(seed_name)

    def _get_content(
        self, path: Path, variables: dict[str, str], *, is_template: bool
    ) -> str:
        if is_template:
            return Template(
                path.read_text(),
                undefined=StrictUndefined,
                keep_trailing_newline=True,
            ).render(**variables)
        return path.read_text()

    def _get_content_hash(
        self, path: Path, variables: dict[str, str], *, is_template: bool
    ) -> bytes:
        if is_template:
            return sha256(
                self._get_content(path, variables, is_template=is_template).encode()
            ).digest()
        return sha256(path.read_bytes()).digest()

    def _should_skip(
        self, seed: Path, crop: Path, variables: dict[str, str], *, is_template: bool
    ) -> bool:
        if not crop.exists():
            return False
        if not self.allow_symlinks and crop.is_symlink():
            return False
        seed_hash = self._get_content_hash(seed, variables, is_template=is_template)
        crop_hash = self._get_content_hash(crop, variables, is_template=False)
        return seed_hash == crop_hash

    def _plant_crop(
        self, seed: Path, crop: Path, variables: dict[str, str], *, is_template: bool
    ) -> None:
        crop.unlink(missing_ok=True)
        content = self._get_content(seed, variables, is_template=is_template)
        crop.write_text(content)

    def sow_granary(
        self, granary_path: Path, templates: set[Path], variables: dict[str, str]
    ) -> None:
        for seed in granary_path.rglob("*"):
            if seed.is_dir():
                continue
            is_template = seed in templates
            crop = self._get_crop_path(granary_path, seed, is_template=is_template)
            if self._should_skip(seed, crop, variables, is_template=is_template):
                continue
            if self.dry_run:
                SGRString(f"Would copy {seed} to {crop}", prefix="☑️ ").print()
                continue

            self._plant_crop(seed, crop, variables, is_template=is_template)

    def run(self) -> None:
        for config in self.config:
            self.sow_granary(
                granary_path=config["granary"],
                templates=config["templates"],
                variables=config["variables"],
            )
