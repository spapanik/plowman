from __future__ import annotations

from difflib import unified_diff
from hashlib import sha256
from typing import TYPE_CHECKING
from unittest import case

from jinja2 import StrictUndefined, Template
from pyutilkit.term import SGRCodes, SGRString

from plowman.commands.base import BaseCommand
from plowman.lib.constants import HOME
from plowman.lib.estate import Estate

if TYPE_CHECKING:
    from pathlib import Path


class SowCommand(BaseCommand):
    __slots__ = ("dry_run", "estate", "verbosity")

    def __init__(self, verbosity: int, *, dry_run: bool) -> None:
        super().__init__()
        self.verbosity = verbosity
        self.dry_run = dry_run
        self.estate = Estate(self.config)

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

    def show_diff(
        self, seed: Path, crop: Path, variables: dict[str, str], *, is_template: bool
    ) -> None:
        seed_content = self._get_content(seed, variables, is_template=is_template)
        crop_content = self._get_content(crop, variables, is_template=False)
        diff = unified_diff(
            crop_content.splitlines(keepends=True),
            seed_content.splitlines(keepends=True),
            fromfile=str(seed),
            tofile=str(crop),
        )
        prefix = " " * 4
        for line in diff:
            if line.startswith("@@"):
                SGRString(line, prefix=prefix, params=[SGRCodes.CYAN]).print(end="")
            elif line.startswith(("+++", "---")):
                SGRString(
                    line, prefix=prefix, params=[SGRCodes.YELLOW, SGRCodes.BOLD]
                ).print(end="")
                continue
            elif line.startswith("+"):
                SGRString(line, prefix=prefix, params=[SGRCodes.GREEN]).print(end="")
            elif line.startswith("-"):
                SGRString(line, prefix=prefix, params=[SGRCodes.RED]).print(end="")
            else:
                SGRString(line, prefix=prefix).print(end="")

    def sow_granary(
        self,
        granary_path: Path,
        templates: set[Path],
        variables: dict[str, str],
        estate_path: Path,
        pending_removal: set[Path],
    ) -> None:
        for seed in granary_path.rglob("*"):
            if seed.is_dir():
                continue
            is_template = seed in templates
            crop = self._get_crop_path(granary_path, seed, is_template=is_template)
            pending_removal.discard(crop)
            self.estate.add(crop, estate_path)
            if self._should_skip(seed, crop, variables, is_template=is_template):
                continue
            if self.dry_run:
                SGRString(f"Would copy {seed} to {crop}", prefix="☑️ ").print()
                if self.verbosity:
                    self.show_diff(seed, crop, variables, is_template=is_template)
                continue
            if self.verbosity:
                SGRString(f"Copying {seed} to {crop}", prefix="☑️ ").print()
                if self.verbosity > 1:
                    self.show_diff(seed, crop, variables, is_template=is_template)

            self._plant_crop(seed, crop, variables, is_template=is_template)

    def run(self) -> None:
        pending_removal = self.estate.current()
        for config in self.config:
            self.sow_granary(
                granary_path=config["granary"],
                templates=config["templates"],
                variables=config["variables"],
                estate_path=config["estate"],
                pending_removal=pending_removal,
            )
        for crop in pending_removal:
            if self.dry_run:
                SGRString(f"Would delete {crop}", prefix="🧹 ").print()
                continue
            if self.verbosity:
                SGRString(f"Deleting {crop}", prefix="🧹 ").print()
            crop.unlink(missing_ok=True)
            self.estate.remove(crop)
        if not self.dry_run:
            self.estate.set_state()
