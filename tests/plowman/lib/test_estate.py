from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from plowman.lib.estate import Estate

if TYPE_CHECKING:
    from plowman.lib.type_defs import Node, ParsedConfig


def test_estate_contains(fake_config: list[ParsedConfig]) -> None:
    estate = Estate(fake_config)
    assert Path("/any/path") in estate


def test_estate_build_tree_empty(fake_config: list[ParsedConfig]) -> None:
    estate = Estate(fake_config)
    tree = estate._build_tree([])
    assert tree == []


def test_estate_build_tree_files_and_dirs(fake_config: list[ParsedConfig]) -> None:
    estate = Estate(fake_config)
    paths = [Path("file1.txt"), Path("dir1/file2.txt"), Path("dir1/dir2/file3.txt")]
    tree = estate._build_tree(paths)
    assert isinstance(tree, list)
    assert "file1.txt" in tree
    assert {"dir1": ["file2.txt", {"dir2": ["file3.txt"]}]} in tree


def test_estate_write_and_parse(
    tmp_path: Path, fake_config: list[ParsedConfig]
) -> None:
    estate = Estate(fake_config)
    test_paths = [Path("file1.txt"), Path("dir1/file2.txt")]
    tree = estate._build_tree(test_paths)
    estate_path = tmp_path / "test_estate.yml"
    estate._write_estate(estate_path, tree)

    parsed_paths = list(estate._parse_estate(estate_path))
    assert Path("file1.txt") in parsed_paths
    assert Path("dir1/file2.txt") in parsed_paths


def test_estate_get_state_empty(fake_config: list[ParsedConfig]) -> None:
    estate = Estate(fake_config)
    state = estate.get_state()
    assert state == {}


def test_estate_add_remove_current(
    tmp_path: Path, fake_config: list[ParsedConfig]
) -> None:
    estate = Estate(fake_config)
    crop = tmp_path / "crop.txt"
    estate.add(crop, tmp_path / "estate.yml")
    assert crop in estate.current()
    estate.remove(crop)
    assert crop not in estate.current()


def test_estate_set_state(tmp_path: Path, fake_config: list[ParsedConfig]) -> None:
    estate = Estate(fake_config)
    estate_path = tmp_path / "test_set_state.yml"
    estate.add(Path("file1.txt"), estate_path)
    estate.set_state()

    parsed_paths = list(estate._parse_estate(estate_path))
    assert Path("file1.txt") in parsed_paths


def test_estate_extract_paths_dict_branch(fake_config: list[ParsedConfig]) -> None:
    """Test _extract_paths with dict node to cover line 64->exit branch."""
    estate = Estate(fake_config)

    node: Node = {"dir1": ["file1.txt", {"dir2": ["file2.txt"]}]}
    paths = list(estate._extract_paths(node))

    assert Path("dir1/file1.txt") in paths
    assert Path("dir1/dir2/file2.txt") in paths


def test_estate_get_crops_by_estate(
    tmp_path: Path, fake_config: list[ParsedConfig]
) -> None:
    """Test get_crops_by_estate returns crops for specific estate."""
    estate = Estate(fake_config)
    estate_path1 = tmp_path / "estate1.yml"
    estate_path2 = tmp_path / "estate2.yml"

    crop1 = tmp_path / "crop1.txt"
    crop2 = tmp_path / "crop2.txt"
    crop3 = tmp_path / "crop3.txt"

    estate.add(crop1, estate_path1)
    estate.add(crop2, estate_path1)
    estate.add(crop3, estate_path2)

    # Get crops for estate_path1
    crops1 = estate.get_crops_by_estate(estate_path1)
    assert crop1 in crops1
    assert crop2 in crops1
    assert crop3 not in crops1

    # Get crops for estate_path2
    crops2 = estate.get_crops_by_estate(estate_path2)
    assert crop3 in crops2
    assert crop1 not in crops2
    assert crop2 not in crops2

    # Get crops for non-existent estate
    crops_empty = estate.get_crops_by_estate(tmp_path / "nonexistent.yml")
    assert crops_empty == set()
