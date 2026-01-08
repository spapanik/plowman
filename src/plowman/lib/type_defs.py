from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from pathlib import Path

Node = str | list["Node"] | dict[str, "Node"]


class ParsedConfig(TypedDict):
    estate: Path
    granary: Path
    variables: dict[str, str]
    templates: set[Path]


class PlowmanConfig(TypedDict, total=False):
    granaries: list[str]
    variables: dict[str, str]
