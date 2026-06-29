from __future__ import annotations

import warnings
from difflib import unified_diff
from hashlib import sha256
from pathlib import Path

from pyutilkit.term import SGRCodes, SGRString

from plowman.commands.base import BaseCommand
from plowman.lib.constants import HOME
from plowman.lib.estate import Estate


class HarvestCommand(BaseCommand):
    __slots__ = ("add_to_estate", "dry_run", "estate", "verbosity")

    def __init__(
        self, verbosity: int, *, dry_run: bool, add_to_estate: list[str]
    ) -> None:
        super().__init__()
        self.verbosity = verbosity
        self.dry_run = dry_run
        self.add_to_estate = add_to_estate
        self.estate = Estate(self.config)

    def _process_add_to_estate(self, add_to_estate: list[str]) -> None:
        """Process --add-to-estate arguments in format granary_name::path."""
        for entry in add_to_estate:
            if "::" not in entry:
                msg = (
                    f"Invalid format for --add-to-estate: '{entry}'. "
                    f"Expected format: granary_name::path"
                )
                raise ValueError(msg)
            granary_name, file_path_str = entry.split("::", 1)
            file_path = Path(file_path_str)

            matched_config = next(
                (config for config in self.config if config["name"] == granary_name),
                None,
            )
            if matched_config is None:
                available_names = ", ".join(
                    c["name"] for c in self.config if c["name"] is not None
                )
                msg = (
                    f"Granary name `{granary_name}` not found. Available names: "
                    f"{available_names or 'none (no named granaries)'}"
                )
                raise ValueError(msg)

            seed = self._get_seed_path(file_path, matched_config["granary"])
            if self.dry_run:
                SGRString(f"Would harvest {file_path} to {seed}", prefix="☑️ ").print()
                continue

            if self.verbosity:
                SGRString(f"Harvesting {file_path} to {seed}", prefix="☑️ ").print()
            self._collect_crop(file_path, seed)

    def _get_seed_path(self, crop: Path, granary: Path) -> Path:
        """Calculate where crop should go in granary."""
        relative_path = crop.relative_to(HOME)
        return granary.joinpath(relative_path)

    def _is_template_seed(self, seed: Path, templates: set[Path]) -> bool:
        """Check if a seed path corresponds to a template file."""
        # Check exact match first
        if seed in templates:
            return True
        # Check if adding .j2 suffix matches a template
        j2_version = seed.with_suffix(f"{seed.suffix}.j2")
        return j2_version in templates

    def _get_content_hash(self, path: Path, *, is_template: bool) -> bytes:
        """Compute SHA256 hash of file content."""
        if not path.exists():
            return b""
        if is_template:
            # For templates in harvest, we read the rendered version from HOME
            # which doesn't have .j2 extension
            return sha256(path.read_bytes()).digest()
        return sha256(path.read_bytes()).digest()

    def _should_harvest(self, crop: Path, seed: Path) -> bool:
        """Check if crop differs from seed. Return True if harvest needed."""
        if not crop.exists():
            return False
        if not seed.exists():
            return True  # Seed doesn't exist, need to create it
        crop_hash = self._get_content_hash(crop, is_template=False)
        seed_hash = self._get_content_hash(seed, is_template=False)
        return crop_hash != seed_hash

    def _collect_crop(self, crop: Path, seed: Path) -> None:
        """Copy crop back to granary location."""
        seed.parent.mkdir(parents=True, exist_ok=True)
        seed.unlink(missing_ok=True)
        content = crop.read_text()
        seed.write_text(content)

    def show_diff(self, crop: Path, seed: Path) -> None:
        """Show unified diff between seed (granary) and crop (home)."""
        seed_content = seed.read_text() if seed.exists() else ""
        crop_content = crop.read_text() if crop.exists() else ""
        diff = unified_diff(
            seed_content.splitlines(keepends=True),
            crop_content.splitlines(keepends=True),
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
            elif line.startswith("+"):
                SGRString(line, prefix=prefix, params=[SGRCodes.GREEN]).print(end="")
            elif line.startswith("-"):
                SGRString(line, prefix=prefix, params=[SGRCodes.RED]).print(end="")
            else:
                SGRString(line, prefix=prefix).print(end="")

    def harvest_granary(
        self,
        granary_path: Path,
        templates: set[Path],
        estate_path: Path,
        pending_harvest: set[Path],
    ) -> None:
        """Harvest changed files from HOME back to granary."""
        # Get all crops managed by this estate
        estate_crops = self.estate.get_crops_by_estate(estate_path)

        for crop in estate_crops:
            if not crop.exists():
                # File no longer exists in HOME, skip
                continue

            pending_harvest.discard(crop)

            # Calculate seed path in granary
            seed = self._get_seed_path(crop, granary_path)

            # Check if this seed actually exists in this granary
            # If not, skip this granary for this crop
            is_template = self._is_template_seed(seed, templates)
            seed_to_check = (
                seed.with_suffix(f"{seed.suffix}.j2")
                if is_template and not seed.exists()
                else seed
            )

            if not seed_to_check.exists():
                # This crop doesn't belong to this granary, skip
                continue

            # Check if this corresponds to a template
            if is_template and not seed.exists():
                # Try with .j2 suffix
                seed = seed_to_check

            # Skip templates - cannot harvest rendered templates back
            if is_template:
                if self._should_harvest(crop, seed):
                    msg = (
                        f"Skipping template file {crop} - "
                        "cannot harvest rendered templates"
                    )
                    warnings.warn(msg, UserWarning, stacklevel=2)
                continue

            if not self._should_harvest(crop, seed):
                continue

            if self.dry_run:
                SGRString(f"Would harvest {crop} to {seed}", prefix="☑️ ").print()
                if self.verbosity:
                    self.show_diff(crop, seed)
                continue

            if self.verbosity:
                SGRString(f"Harvesting {crop} to {seed}", prefix="☑️ ").print()
                if self.verbosity > 1:
                    self.show_diff(crop, seed)

            self._collect_crop(crop, seed)

    def run(self) -> None:
        """Execute the harvest command."""
        self._process_add_to_estate(self.add_to_estate)
        pending_harvest = self.estate.current()
        for config in self.config:
            self.harvest_granary(
                granary_path=config["granary"],
                templates=config["templates"],
                estate_path=config["estate"],
                pending_harvest=pending_harvest,
            )
        if not self.dry_run:
            self.estate.set_state()
