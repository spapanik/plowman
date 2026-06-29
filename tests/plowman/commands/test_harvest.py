from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import mock

import pytest

from plowman.commands.harvest import HarvestCommand

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def harvest_command(tmp_path: Path) -> HarvestCommand:
    config_path = tmp_path / "config.yml"
    granary_dir = tmp_path / "granary"
    granary_dir.mkdir()
    estate_file = tmp_path / "estate.yml"
    templates: set[Path] = set()
    variables: dict[str, str] = {}
    name = "test_granary"

    config_data = [
        {
            "estate": estate_file,
            "granary": granary_dir,
            "templates": templates,
            "variables": variables,
            "name": name,
        }
    ]

    with (
        mock.patch(
            "plowman.commands.base.BaseCommand._get_config", return_value=config_data
        ),
        mock.patch("plowman.lib.constants.CONFIG_PATH", config_path),
    ):
        return HarvestCommand(verbosity=0, dry_run=True, add_to_estate=[])


def test_harvest_command_init(harvest_command: HarvestCommand) -> None:
    assert harvest_command.verbosity == 0
    assert harvest_command.dry_run is True
    assert harvest_command.add_to_estate == []


def test_get_seed_path(harvest_command: HarvestCommand, tmp_path: Path) -> None:
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "subdir" / "file.txt"
    crop.parent.mkdir(exist_ok=True)
    crop.write_text("content")

    granary = tmp_path / "granary"
    granary.mkdir(exist_ok=True)

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        seed = harvest_command._get_seed_path(crop, granary)

    assert seed == granary / "subdir" / "file.txt"


def test_should_harvest_no_changes(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    crop = tmp_path / "crop.txt"
    crop.write_text("content")
    seed = tmp_path / "seed.txt"
    seed.write_text("content")

    should_harvest = harvest_command._should_harvest(crop, seed)
    assert should_harvest is False


def test_should_harvest_with_changes(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    crop = tmp_path / "crop.txt"
    crop.write_text("new content")
    seed = tmp_path / "seed.txt"
    seed.write_text("old content")

    should_harvest = harvest_command._should_harvest(crop, seed)
    assert should_harvest is True


def test_should_harvest_missing_seed(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    crop = tmp_path / "crop.txt"
    crop.write_text("content")
    seed = tmp_path / "seed.txt"

    should_harvest = harvest_command._should_harvest(crop, seed)
    assert should_harvest is True


def test_should_harvest_missing_crop(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    crop = tmp_path / "crop.txt"
    seed = tmp_path / "seed.txt"
    seed.write_text("content")

    should_harvest = harvest_command._should_harvest(crop, seed)
    assert should_harvest is False


def test_collect_crop(harvest_command: HarvestCommand, tmp_path: Path) -> None:
    crop = tmp_path / "crop.txt"
    crop.write_text("content")
    seed = tmp_path / "seed.txt"

    harvest_command._collect_crop(crop, seed)
    assert seed.read_text() == "content"


def test_collect_crop_creates_directories(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    crop = tmp_path / "crop.txt"
    crop.write_text("content")
    seed = tmp_path / "subdir" / "seed.txt"

    harvest_command._collect_crop(crop, seed)
    assert seed.exists()
    assert seed.read_text() == "content"


def test_show_diff(
    harvest_command: HarvestCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    seed = tmp_path / "seed.txt"
    seed.write_text("old line\n")
    crop = tmp_path / "crop.txt"
    crop.write_text("new line\n")

    harvest_command.show_diff(crop, seed)
    captured = capsys.readouterr()
    assert "-old line" in captured.out or "+new line" in captured.out


def test_show_diff_missing_seed(
    harvest_command: HarvestCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    seed = tmp_path / "seed.txt"
    crop = tmp_path / "crop.txt"
    crop.write_text("new line\n")

    harvest_command.show_diff(crop, seed)
    captured = capsys.readouterr()
    assert "+new line" in captured.out


def test_is_template_seed(harvest_command: HarvestCommand, tmp_path: Path) -> None:
    granary = tmp_path / "granary"
    # granary already exists from fixture
    template = granary / "file.txt.j2"
    template.write_text("template")
    templates = {template}

    seed = granary / "file.txt"
    assert harvest_command._is_template_seed(seed, templates) is True


def test_is_template_seed_exact_match(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    granary = tmp_path / "granary"
    # granary already exists from fixture
    template = granary / "file.txt"
    template.write_text("content")
    templates = {template}

    assert harvest_command._is_template_seed(template, templates) is True


def test_is_template_seed_no_match(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    granary = tmp_path / "granary"
    # granary already exists from fixture
    templates: set[Path] = set()

    seed = granary / "file.txt"
    assert harvest_command._is_template_seed(seed, templates) is False


def test_harvest_granary_dry_run(
    harvest_command: HarvestCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    granary = tmp_path / "granary"
    # granary already exists from fixture
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "file.txt"
    crop.write_text("modified content")

    seed = granary / "file.txt"
    seed.write_text("original content")

    estate_file = tmp_path / "estate.yml"
    harvest_command.estate._state = {crop: estate_file}
    pending_harvest: set[Path] = {crop}

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command.harvest_granary(granary, set(), estate_file, pending_harvest)

    captured = capsys.readouterr()
    assert "Would harvest" in captured.out
    # Seed should not be modified in dry run
    assert seed.read_text() == "original content"


def test_harvest_granary_actual(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    harvest_command.dry_run = False
    granary = tmp_path / "granary"
    # granary already exists from fixture
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "file.txt"
    crop.write_text("modified content")

    seed = granary / "file.txt"
    seed.write_text("original content")

    estate_file = tmp_path / "estate.yml"
    harvest_command.estate._state = {crop: estate_file}
    pending_harvest: set[Path] = {crop}

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command.harvest_granary(granary, set(), estate_file, pending_harvest)

    assert seed.read_text() == "modified content"


def test_harvest_granary_verbose(
    harvest_command: HarvestCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    harvest_command.dry_run = False
    harvest_command.verbosity = 1
    granary = tmp_path / "granary"
    # granary already exists from fixture
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "file.txt"
    crop.write_text("modified content")

    seed = granary / "file.txt"
    seed.write_text("original content")

    estate_file = tmp_path / "estate.yml"
    harvest_command.estate._state = {crop: estate_file}
    pending_harvest: set[Path] = {crop}

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command.harvest_granary(granary, set(), estate_file, pending_harvest)

    captured = capsys.readouterr()
    assert "Harvesting" in captured.out


def test_harvest_granary_very_verbose(
    harvest_command: HarvestCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    harvest_command.dry_run = False
    harvest_command.verbosity = 2
    granary = tmp_path / "granary"
    # granary already exists from fixture
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "file.txt"
    crop.write_text("modified content")

    seed = granary / "file.txt"
    seed.write_text("original content")

    estate_file = tmp_path / "estate.yml"
    harvest_command.estate._state = {crop: estate_file}
    pending_harvest: set[Path] = {crop}

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command.harvest_granary(granary, set(), estate_file, pending_harvest)

    captured = capsys.readouterr()
    assert "Harvesting" in captured.out
    assert "-original content" in captured.out or "+modified content" in captured.out


def test_harvest_granary_skip_same_content(
    harvest_command: HarvestCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    granary = tmp_path / "granary"
    # granary already exists from fixture
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "file.txt"
    crop.write_text("same content")

    seed = granary / "file.txt"
    seed.write_text("same content")

    estate_file = tmp_path / "estate.yml"
    harvest_command.estate._state = {crop: estate_file}
    pending_harvest: set[Path] = {crop}

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command.harvest_granary(granary, set(), estate_file, pending_harvest)

    captured = capsys.readouterr()
    assert "Would harvest" not in captured.out


def test_harvest_granary_skip_missing_crop(
    harvest_command: HarvestCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    granary = tmp_path / "granary"
    # granary already exists from fixture
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "file.txt"
    # Don't create crop - it doesn't exist

    estate_file = tmp_path / "estate.yml"
    harvest_command.estate._state = {crop: estate_file}
    pending_harvest: set[Path] = {crop}

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command.harvest_granary(granary, set(), estate_file, pending_harvest)

    captured = capsys.readouterr()
    assert "Would harvest" not in captured.out


def test_process_add_to_estate_valid(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    """Test that --add-to-estate copies into the granary without tracking it."""
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    test_file = home_dir / "test.txt"
    test_file.write_text("content")
    harvest_command.dry_run = False

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command._process_add_to_estate([f"test_granary::{test_file}"])

    assert (tmp_path / "granary" / "test.txt").read_text() == "content"
    assert test_file not in harvest_command.estate._state


def test_process_add_to_estate_verbose(
    harvest_command: HarvestCommand,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    test_file = home_dir / "test.txt"
    test_file.write_text("content")
    harvest_command.dry_run = False
    harvest_command.verbosity = 1

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command._process_add_to_estate([f"test_granary::{test_file}"])

    assert f"Harvesting {test_file}" in capsys.readouterr().out


def test_process_add_to_estate_dry_run(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    test_file = home_dir / "test.txt"
    test_file.write_text("content")

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command._process_add_to_estate([f"test_granary::{test_file}"])

    assert not (tmp_path / "granary" / "test.txt").exists()
    assert test_file not in harvest_command.estate._state


def test_process_add_to_estate_invalid_format(
    harvest_command: HarvestCommand,
) -> None:
    """Test processing invalid --add-to-estate format."""
    with pytest.raises(ValueError, match="Invalid format"):
        harvest_command._process_add_to_estate(["invalid_path"])


def test_process_add_to_estate_unknown_granary(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    """Test processing --add-to-estate with unknown granary name."""
    test_file = tmp_path / "test.txt"
    with pytest.raises(ValueError, match="Granary name `unknown` not found"):
        harvest_command._process_add_to_estate([f"unknown::{test_file}"])


def test_run_dry_run(harvest_command: HarvestCommand, tmp_path: Path) -> None:
    estate_file = tmp_path / "estate.yml"
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "crop.txt"
    crop.write_text("content")

    harvest_command.estate._state = {crop: estate_file}

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command.run()

    assert not estate_file.exists()


def test_run_actual(harvest_command: HarvestCommand, tmp_path: Path) -> None:
    harvest_command.dry_run = False
    estate_file = tmp_path / "estate.yml"
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "crop.txt"
    crop.write_text("content")

    harvest_command.estate._state = {crop: estate_file}

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command.run()

    assert estate_file.exists()


def test_run_updates_estate(harvest_command: HarvestCommand, tmp_path: Path) -> None:
    """Test that run() updates estate state."""
    harvest_command.dry_run = False
    estate_file = tmp_path / "estate.yml"
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "crop.txt"
    crop.write_text("content")

    harvest_command.estate._state = {crop: estate_file}

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command.run()

    # Verify estate was updated
    assert estate_file.exists()
    # Reload and check state
    harvest_command.estate._state = harvest_command.estate.get_state()
    assert crop in harvest_command.estate.current()


def test_get_content_hash_nonexistent(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    """Test _get_content_hash with nonexistent file."""
    path = tmp_path / "nonexistent.txt"
    hash_val = harvest_command._get_content_hash(path, is_template=False)
    assert hash_val == b""


def test_get_content_hash_template(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    """Test _get_content_hash with template flag."""
    path = tmp_path / "template.txt"
    path.write_text("content")
    hash_val = harvest_command._get_content_hash(path, is_template=True)
    assert isinstance(hash_val, bytes)
    assert len(hash_val) > 0


def test_show_diff_context_line(
    harvest_command: HarvestCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test show_diff with context lines (unchanged lines)."""
    seed = tmp_path / "seed.txt"
    seed.write_text("line1\nline2\nline3\n")
    crop = tmp_path / "crop.txt"
    crop.write_text("line1\nmodified\nline3\n")

    harvest_command.show_diff(crop, seed)
    captured = capsys.readouterr()
    # Context line should be present
    assert " line1" in captured.out or " line3" in captured.out


def test_harvest_granary_template_with_j2_suffix(
    harvest_command: HarvestCommand, tmp_path: Path
) -> None:
    """Test that template files are skipped with a warning."""
    harvest_command.dry_run = False
    granary = tmp_path / "granary"
    # granary already exists from fixture
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "file.txt"
    crop.write_text("modified content")

    # Template in granary has .j2 suffix
    seed = granary / "file.txt.j2"
    seed.write_text("original content")
    templates = {seed}

    estate_file = tmp_path / "estate.yml"
    harvest_command.estate._state = {crop: estate_file}
    pending_harvest: set[Path] = {crop}

    with (
        mock.patch("plowman.commands.harvest.HOME", home_dir),
        pytest.warns(UserWarning, match="Skipping template file.*cannot harvest"),
    ):
        harvest_command.harvest_granary(
            granary, templates, estate_file, pending_harvest
        )

    # Template should NOT be updated (skipped)
    assert seed.read_text() == "original content"


def test_harvest_granary_template_unchanged(
    harvest_command: HarvestCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that unchanged template files are skipped silently."""
    harvest_command.dry_run = False
    granary = tmp_path / "granary"
    # granary already exists from fixture
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "file.txt"
    crop.write_text("same content")

    # Template in granary has .j2 suffix
    seed = granary / "file.txt.j2"
    seed.write_text("same content")
    templates = {seed}

    estate_file = tmp_path / "estate.yml"
    harvest_command.estate._state = {crop: estate_file}
    pending_harvest: set[Path] = {crop}

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command.harvest_granary(
            granary, templates, estate_file, pending_harvest
        )

    # Template should NOT be updated (skipped)
    assert seed.read_text() == "same content"

    # No warning should be printed (files are identical)
    captured = capsys.readouterr()
    assert captured.err == ""


def test_harvest_granary_verbose_dry_run_with_diff(
    harvest_command: HarvestCommand, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test verbose dry run shows diff."""
    harvest_command.verbosity = 1
    granary = tmp_path / "granary"
    # granary already exists from fixture
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    crop = home_dir / "file.txt"
    crop.write_text("modified content")

    seed = granary / "file.txt"
    seed.write_text("original content")

    estate_file = tmp_path / "estate.yml"
    harvest_command.estate._state = {crop: estate_file}
    pending_harvest: set[Path] = {crop}

    with mock.patch("plowman.commands.harvest.HOME", home_dir):
        harvest_command.harvest_granary(granary, set(), estate_file, pending_harvest)

    captured = capsys.readouterr()
    assert "Would harvest" in captured.out
    assert "-original content" in captured.out or "+modified content" in captured.out
