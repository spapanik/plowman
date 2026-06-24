from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

    from plowman.lib.type_defs import ParsedConfig


@pytest.fixture
def fake_config(tmp_path: Path) -> list[ParsedConfig]:
    return [
        {
            "estate": tmp_path / "estate.yml",
            "granary": tmp_path / "granary",
            "templates": {tmp_path / "granary" / "templates.jinja"},
            "variables": {"owner": "test-owner"},
        }
    ]
