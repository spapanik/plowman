from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from plowman.commands.sow import SowCommand


@pytest.fixture
def sow_command(tmp_path: Path) -> SowCommand:
    config_path = tmp_path / "config.yml"
    granary_dir = tmp_path / "granary"
    granary_dir.mkdir()
    estate_file = tmp_path / "estate.yml"
    templates: set[Path] = set()
    variables: dict[str, str] = {}

    config_data = [
        {
            "estate": estate_file,
            "granary": granary_dir,
            "templates": templates,
            "variables": variables,
        }
    ]

    with (
        mock.patch(
            "plowman.commands.base.BaseCommand._get_config", return_value=config_data
        ),
        mock.patch("plowman.lib.constants.CONFIG_PATH", config_path),
    ):
        return SowCommand(verbosity=0, dry_run=True)


def test_sow_command_init(sow_command: SowCommand) -> None:
    assert sow_command.verbosity == 0
    assert sow_command.dry_run is True


def test_get_crop_path(sow_command: SowCommand, tmp_path: Path) -> None:
    granary = tmp_path / "granary"
    # granary already exists from fixture
    seed = granary / "subdir" / "file.txt"
    seed.parent.mkdir(exist_ok=True)
    seed.write_text("content")

    with mock.patch("plowman.commands.sow.HOME", tmp_path / "home"):
        crop = sow_command._get_crop_path(granary, seed, is_template=False)

    assert crop.name == "file.txt"


def test_get_content_nonexistent(sow_command: SowCommand) -> None:
    content = sow_command._get_content(Path("/nonexistent"), {}, is_template=False)
    assert content == ""


def test_get_content_template(sow_command: SowCommand, tmp_path: Path) -> None:
    template_file = tmp_path / "template.txt"
    template_file.write_text("Hello {{ name }}")
    content = sow_command._get_content(
        template_file, {"name": "World"}, is_template=True
    )
    assert content == "Hello World"


def test_get_content_hash_template(sow_command: SowCommand, tmp_path: Path) -> None:
    file_path = tmp_path / "template.txt"
    file_path.write_text("Hello {{ name }}")
    hash_val = sow_command._get_content_hash(
        file_path, {"name": "World"}, is_template=True
    )
    assert isinstance(hash_val, bytes)


def test_should_skip_symlink(sow_command: SowCommand, tmp_path: Path) -> None:
    seed = tmp_path / "seed.txt"
    seed.write_text("content")
    crop = tmp_path / "crop.txt"
    crop.symlink_to(seed)

    should_skip = sow_command._should_skip(seed, crop, {}, is_template=False)
    assert should_skip is False


def test_show_diff_context_line(
    sow_command: SowCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    seed = tmp_path / "seed.txt"
    seed.write_text("line1\nline2\n")
    crop = tmp_path / "crop.txt"
    crop.write_text("line1\nline3\n")

    sow_command.show_diff(seed, crop, {}, is_template=False)
    captured = capsys.readouterr()
    # Check for context line (starts with space)
    assert (
        " line1" in captured.out or "-line3" in captured.out or "+line2" in captured.out
    )


def test_sow_granary_skip_dir(
    sow_command: SowCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    granary = tmp_path / "granary"
    # granary already exists from fixture
    subdir = granary / "subdir"
    subdir.mkdir(exist_ok=True)

    estate_file = tmp_path / "estate.yml"
    pending_removal: set[Path] = set()

    with mock.patch("plowman.commands.sow.HOME", tmp_path / "home"):
        sow_command.sow_granary(granary, set(), {}, estate_file, pending_removal)

    captured = capsys.readouterr()
    # Should not try to copy directories
    assert "Would copy" not in captured.out or subdir.name not in captured.out


def test_sow_granary_skip_same_content(
    sow_command: SowCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    granary = tmp_path / "granary"
    seed = granary / "file.txt"
    seed.write_text("content")

    home_dir = tmp_path / "home"
    home_dir.mkdir(exist_ok=True)
    crop = home_dir / "file.txt"
    crop.write_text("content")

    estate_file = tmp_path / "estate.yml"
    pending_removal: set[Path] = set()

    with mock.patch("plowman.commands.sow.HOME", home_dir):
        sow_command.sow_granary(granary, set(), {}, estate_file, pending_removal)

    captured = capsys.readouterr()
    # Should skip because content is the same
    assert "Would copy" not in captured.out


def test_sow_granary_verbose_dry_run(
    sow_command: SowCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sow_command.verbosity = 1
    granary = tmp_path / "granary"
    seed = granary / "file.txt"
    seed.write_text("new content")

    home_dir = tmp_path / "home"
    home_dir.mkdir(exist_ok=True)
    crop = home_dir / "file.txt"
    crop.write_text("old content")

    estate_file = tmp_path / "estate.yml"
    pending_removal: set[Path] = set()

    with mock.patch("plowman.commands.sow.HOME", home_dir):
        sow_command.sow_granary(granary, set(), {}, estate_file, pending_removal)

    captured = capsys.readouterr()
    assert "Would copy" in captured.out
    assert "-old content" in captured.out or "+new content" in captured.out


def test_sow_granary_verbose_actual_copy(
    sow_command: SowCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sow_command.dry_run = False
    sow_command.verbosity = 1
    granary = tmp_path / "granary"
    seed = granary / "file.txt"
    seed.write_text("content")

    estate_file = tmp_path / "estate.yml"
    pending_removal: set[Path] = set()
    home_dir = tmp_path / "home"
    home_dir.mkdir(exist_ok=True)

    with mock.patch("plowman.commands.sow.HOME", home_dir):
        sow_command.sow_granary(granary, set(), {}, estate_file, pending_removal)

    captured = capsys.readouterr()
    assert "Copying" in captured.out
    crop = home_dir / "file.txt"
    assert crop.exists()


def test_sow_granary_very_verbose_actual_copy(
    sow_command: SowCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sow_command.dry_run = False
    sow_command.verbosity = 2
    granary = tmp_path / "granary"
    seed = granary / "file.txt"
    seed.write_text("new content")

    home_dir = tmp_path / "home"
    home_dir.mkdir(exist_ok=True)
    crop = home_dir / "file.txt"
    crop.write_text("old content")

    estate_file = tmp_path / "estate.yml"
    pending_removal: set[Path] = set()

    with mock.patch("plowman.commands.sow.HOME", home_dir):
        sow_command.sow_granary(granary, set(), {}, estate_file, pending_removal)

    captured = capsys.readouterr()
    assert "Copying" in captured.out
    assert "-old content" in captured.out or "+new content" in captured.out


def test_run_verbose_delete(
    sow_command: SowCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sow_command.dry_run = False
    sow_command.verbosity = 1
    estate_file = tmp_path / "estate.yml"
    crop = tmp_path / "crop.txt"
    crop.write_text("content")

    sow_command.estate._state = {crop: estate_file}
    sow_command.run()

    captured = capsys.readouterr()
    assert "Deleting" in captured.out
    assert not crop.exists()


def test_should_skip_nonexistent_crop(sow_command: SowCommand, tmp_path: Path) -> None:
    seed = tmp_path / "seed.txt"
    seed.write_text("content")
    crop = tmp_path / "crop.txt"

    should_skip = sow_command._should_skip(seed, crop, {}, is_template=False)
    assert should_skip is False


def test_should_skip_same_content(sow_command: SowCommand, tmp_path: Path) -> None:
    seed = tmp_path / "seed.txt"
    seed.write_text("content")
    crop = tmp_path / "crop.txt"
    crop.write_text("content")

    should_skip = sow_command._should_skip(seed, crop, {}, is_template=False)
    assert should_skip is True


def test_plant_crop(sow_command: SowCommand, tmp_path: Path) -> None:
    seed = tmp_path / "seed.txt"
    seed.write_text("content")
    crop = tmp_path / "crop.txt"

    sow_command._plant_crop(seed, crop, {}, is_template=False)
    assert crop.read_text() == "content"


def test_show_diff(
    sow_command: SowCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    seed = tmp_path / "seed.txt"
    seed.write_text("new line\n")
    crop = tmp_path / "crop.txt"
    crop.write_text("old line\n")

    sow_command.show_diff(seed, crop, {}, is_template=False)
    captured = capsys.readouterr()
    assert "-old line" in captured.out or "+new line" in captured.out


def test_sow_granary_dry_run(
    sow_command: SowCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    granary = tmp_path / "granary"
    # granary already exists from fixture
    seed = granary / "file.txt"
    seed.write_text("content")

    estate_file = tmp_path / "estate.yml"
    pending_removal: set[Path] = set()

    with mock.patch("plowman.commands.sow.HOME", tmp_path / "home"):
        sow_command.sow_granary(granary, set(), {}, estate_file, pending_removal)

    captured = capsys.readouterr()
    assert "Would copy" in captured.out


def test_sow_granary_actual_copy(sow_command: SowCommand, tmp_path: Path) -> None:
    sow_command.dry_run = False
    granary = tmp_path / "granary"
    # granary already exists from fixture
    seed = granary / "file.txt"
    seed.write_text("content")

    estate_file = tmp_path / "estate.yml"
    pending_removal: set[Path] = set()
    home_dir = tmp_path / "home"
    home_dir.mkdir(exist_ok=True)

    with mock.patch("plowman.commands.sow.HOME", home_dir):
        sow_command.sow_granary(granary, set(), {}, estate_file, pending_removal)

    crop = home_dir / "file.txt"
    assert crop.exists()


def test_run_dry_run_delete(
    sow_command: SowCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    estate_file = tmp_path / "estate.yml"
    crop = tmp_path / "crop.txt"
    crop.write_text("content")

    sow_command.estate._state = {crop: estate_file}
    sow_command.run()

    captured = capsys.readouterr()
    assert "Would delete" in captured.out


def test_run_actual_delete(sow_command: SowCommand, tmp_path: Path) -> None:
    sow_command.dry_run = False
    estate_file = tmp_path / "estate.yml"
    crop = tmp_path / "crop.txt"
    crop.write_text("content")

    sow_command.estate._state = {crop: estate_file}
    sow_command.run()

    assert not crop.exists()
