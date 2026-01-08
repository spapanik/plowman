from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from dj_settings.settings import ConfigParser
from ruamel.yaml import YAML

if TYPE_CHECKING:
    from collections.abc import Iterator

    from plowman.lib.type_defs import Node, ParsedConfig


class Estate:
    __slots__ = ("_estate_paths", "_state")

    def __init__(self, config: list[ParsedConfig]) -> None:
        self._estate_paths = {config["estate"] for config in config}
        self._state = self.get_state()

    def __contains__(self, path: Path) -> bool:
        return True

    def _build_tree(self, paths: list[Path]) -> Node:
        if not paths:
            return []

        groups: dict[str, list[Path]] = {}
        direct_files: list[str] = []

        for path in paths:
            if len(path.parts) == 1:
                direct_files.append(path.parts[0])
            else:
                first = path.parts[0]
                rest = Path(*path.parts[1:])
                groups.setdefault(first, []).append(rest)

        result: list[Node] = []

        result.extend(sorted(direct_files))

        for dir_name in sorted(groups.keys()):
            subtree = self._build_tree(groups[dir_name])
            result.append({dir_name: subtree})

        return result

    def _write_estate(self, estate: Path, tree: Node) -> None:
        estate.parent.mkdir(parents=True, exist_ok=True)
        yaml = YAML()
        yaml.default_flow_style = False
        with estate.open("w") as file:
            yaml.dump({"files": tree}, file)

    def _extract_paths(self, node: Node, parent: Path = Path()) -> Iterator[Path]:
        if isinstance(node, list):
            for item in node:
                if isinstance(item, str):
                    yield parent.joinpath(item)
                elif isinstance(item, dict):
                    yield from self._extract_paths(item, parent)
        elif isinstance(node, dict):
            for key, value in node.items():
                yield from self._extract_paths(value, parent.joinpath(key))

    def _parse_estate(self, estate: Path) -> Iterator[Path]:
        if not estate.exists():
            return
        yield from self._extract_paths(ConfigParser([estate]).data["files"])

    def get_state(self) -> dict[Path, Path]:
        return {
            file: estate
            for estate in self._estate_paths
            for file in self._parse_estate(estate)
        }

    def set_state(self) -> None:
        estate_files: dict[Path, list[Path]] = {}
        for file, estate in self._state.items():
            estate_files.setdefault(estate, []).append(file)

        for estate, files in estate_files.items():
            tree = self._build_tree(sorted(files))
            self._write_estate(estate, tree)

    def add(self, crop: Path, estate_path: Path) -> None:
        self._state[crop] = estate_path

    def remove(self, crop: Path) -> None:
        self._state.pop(crop, None)

    def current(self) -> set[Path]:
        return set(self._state)
