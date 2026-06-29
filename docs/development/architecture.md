# Architecture Overview

This document explains plowman's internal architecture, design decisions, and code organization.

## High-Level Overview

plowman is a command-line tool built in Python that manages dotfile deployment using an agricultural metaphor. The system consists of several key components working together to read configuration, process files, and maintain state.

### Design Goals

- **Simplicity**: Easy to understand and configure
- **Reliability**: Safe file operations with state tracking
- **Efficiency**: Skip unchanged files using hashing
- **Flexibility**: Support templates and multiple granaries
- **Maintainability**: Clean code structure with clear separation of concerns

## Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     CLI Layer                            │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │ __main__.py  │───▶│  lib/cli.py  │                   │
│  │   (entry)    │    │ (arg parsing)│                   │
│  └──────────────┘    └──────────────┘                   │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  Command Layer                           │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │  BaseCommand     │◀───│   SowCommand     │          │
│  │  (config loading)│    │ (deployment logic)│         │
│  └──────────────────┘    └──────────────────┘          │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
┌──────────────────────┐  ┌──────────────────────┐
│   Config System      │  │   State Management   │
│  ┌────────────────┐  │  │  ┌────────────────┐  │
│  │ dj_settings    │  │  │  │    Estate      │  │
│  │ ConfigParser   │  │  │  │  (tracking)    │  │
│  └────────────────┘  │  │  └────────────────┘  │
└──────────────────────┘  └──────────────────────┘
              │                     │
              ▼                     ▼
┌─────────────────────────────────────────────────────────┐
│                 Template Engine                          │
│  ┌──────────────────┐                                   │
│  │    Jinja2        │                                   │
│  │  (rendering)     │                                   │
│  └──────────────────┘                                   │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
src/plowman/
├── __init__.py           # Package initialization
├── __main__.py           # CLI entry point
├── __version__.py        # Version information
├── commands/             # Command implementations
│   ├── __init__.py
│   ├── base.py          # BaseCommand class
│   └── sow.py           # SowCommand implementation
├── lib/                  # Library modules
│   ├── __init__.py
│   ├── cli.py           # Argument parsing
│   ├── constants.py     # Constants (HOME, CONFIG_PATH)
│   ├── estate.py        # Estate state management
│   ├── exceptions.py    # Custom exceptions
│   └── type_defs.py     # Type definitions
└── ...
```

## Key Components

### 1. Entry Point (`__main__.py`)

The main entry point for the CLI application.

**Responsibilities:**

- Parse command-line arguments
- Route to appropriate command based on subcommand
- Initialize and run the command

**Code flow:**

```python
def main() -> None:
    args = parse_args()                    # Parse CLI args
    match args.subcommand:
        case "sow":
            SowCommand(                    # Create command
                verbosity=args.verbosity,
                dry_run=args.dry_run
            ).run()                        # Execute command
```

### 2. CLI Parsing (`lib/cli.py`)

Handles argument parsing using Python's `argparse`.

**Features:**

- Global flags: `--version`, `--verbose`, `--dry-run`
- Subcommand structure (currently only `sow`)
- Verbosity stacking (`-v`, `-vv`, `-vvv`)
- Returns typed `PlowmanArgs` dataclass

**Key classes:**

```python
@dataclass(frozen=True, slots=True)
class PlowmanArgs:
    subcommand: Literal["sow"]
    verbosity: int
    dry_run: bool
```

### 3. Base Command (`commands/base.py`)

Abstract base class for all commands.

**Responsibilities:**

- Load configuration from `~/.config/plowman/config.yaml`
- Parse granary configurations
- Validate granary paths exist
- Provide common functionality for all commands

**Key methods:**

- `_get_config()`: Loads and parses main config file
- `_parse_config()`: Processes each path's configuration
- `run()`: Abstract method implemented by subclasses

**Configuration loading:**

```python
def _get_config(self) -> list[ParsedConfig]:
    if not CONFIG_PATH.exists():
        raise MissingConfigError
    config_path = ConfigParser([CONFIG_PATH]).data["granaries"]
    return [
        granary_config
        for path, config in config_path.items()
        for granary_config in self._parse_config(Path(path), config)
    ]
```

### 4. Sow Command (`commands/sow.py`)

Main implementation of the dotfile deployment logic.

**Responsibilities:**

- Process all configured granaries
- Render Jinja2 templates
- Deploy files to home directory
- Track state in estate files
- Clean up orphaned files
- Show diffs in verbose mode

**Key methods:**

**`_get_crop_path()`**: Maps seed location to crop location

```python
def _get_crop_path(self, granary: Path, seed: Path, *, is_template: bool) -> Path:
    farm = HOME.joinpath(seed.relative_to(granary)).parent
    farm.mkdir(exist_ok=True, parents=True)
    seed_name = seed.with_suffix("").name if is_template else seed.name
    return farm.joinpath(seed_name)
```

**`_get_content()`**: Reads and renders templates

```python
def _get_content(
    self, path: Path, variables: dict[str, str], *, is_template: bool
) -> str:
    if not path.exists():
        return ""
    if is_template:
        return Template(
            path.read_text(),
            undefined=StrictUndefined,
            keep_trailing_newline=True,
        ).render(**variables)
    return path.read_text()
```

**`_should_skip()`**: Compares hashes to avoid unnecessary writes

```python
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
```

**`show_diff()`**: Displays unified diff with colored output

- Uses `difflib.unified_diff` for diff generation
- Color-codes output using `pyutilkit.term.SGRString`
- Different colors for additions (green), deletions (red), headers (cyan/yellow)

**`sow_granary()`**: Processes all seeds in a granary

- Recursively scans granary directory
- Determines if each file is a template
- Calculates crop path
- Tracks in estate
- Skips unchanged files
- Plants crops (writes files)
- Shows diffs if verbose

**`run()`**: Main execution loop

1. Get current estate state
2. For each config, sow the granary
3. Remove orphaned crops
4. Update estate state

### 5. Estate Management (`lib/estate.py`)

Tracks deployed files for automatic cleanup.

**Responsibilities:**

- Load existing estate from YAML file
- Add/remove tracked files
- Detect orphaned files
- Save updated estate

**Data structure:**

```yaml
files:
    - .bashrc
    - config:
          - nvim:
                - init.vim
```

**Key methods:**

- `current()`: Returns set of currently tracked files
- `add()`: Adds a file to tracking
- `remove()`: Removes a file from tracking
- `set_state()`: Saves estate to disk

### 6. Configuration System

Uses `dj_settings` library for YAML configuration parsing.

**Configuration hierarchy:**

1. **Main config**: `~/.config/plowman/config.yaml`
    - Defines paths and granaries
    - Sets variables for templates

2. **Per-path config**: `{path}/.plowman/plowman.yml`
    - Specifies which files are templates
    - Optional override per path

3. **Estate file**: `{path}/.plowman/estate.yml`
    - Auto-generated state tracking
    - Not user-edited

**Type definitions** (`lib/type_defs.py`):

```python
PlowmanConfig = dict[str, Any]
ParsedConfig = TypedDict('ParsedConfig', {
    'estate': Path,
    'variables': dict[str, str],
    'granary': Path,
    'templates': set[Path],
})
```

## Data Flow

### Deployment Process

```
1. User runs: plm sow
       │
       ▼
2. Parse CLI args (__main__.py)
       │
       ▼
3. Create SowCommand instance
       │
       ▼
4. BaseCommand.__init__() loads config
       │
       ├─▶ Read ~/.config/plowman/config.yaml
       ├─▶ Parse granaries for each path
       └─▶ Read optional .plowman/plowman.yml
       │
       ▼
5. Initialize Estate with current state
       │
       ▼
6. For each granary config:
       │
       ├─▶ Scan all files recursively (seeds)
       ├─▶ For each seed:
       │   ├─▶ Determine if template
       │   ├─▶ Calculate crop path
       │   ├─▶ Track crop in estate
       │   ├─▶ Compare hash - skip if unchanged
       │   ├─▶ Render template if needed
       │   ├─▶ Write to crop location
       │   └─▶ Show diff if verbose
       │
       ▼
7. Remove orphaned crops
       │
       ▼
8. Update estate file
       │
       ▼
9. Exit
```

### Hash Comparison Flow

```
Seed file exists?
    │
    ├─ No → Deploy (file is new)
    │
    └─ Yes
        │
        ▼
Crop file exists?
    │
    ├─ No → Deploy (file is new)
    │
    └─ Yes
        │
        ▼
Allow symlinks?
    │
    ├─ No & Crop is symlink → Deploy (replace symlink)
    │
    └─ Yes or Crop not symlink
        │
        ▼
Calculate seed hash (rendered if template)
        │
        ▼
Calculate crop hash (plain content)
        │
        ▼
Hashes match?
    │
    ├─ Yes → Skip (no changes)
    │
    └─ No → Deploy (file changed)
```

## Agricultural Metaphor Mapping

The code uses agricultural terminology consistently:

| Metaphor     | Code Concept          | Implementation                        |
| ------------ | --------------------- | ------------------------------------- |
| **Granary**  | Source directory      | `Path` object pointing to granary dir |
| **Seed**     | Source file           | Individual file in granary            |
| **Crop**     | Deployed file         | File in home directory                |
| **Farm**     | Destination directory | Parent dir of crop in home            |
| **Estate**   | State tracking        | YAML file tracking crops              |
| **Planting** | File deployment       | Writing content to crop path          |
| **Weeding**  | Cleanup               | Removing orphaned crops               |
| **Sowing**   | Overall process       | The `sow` command                     |

## Error Handling

### Custom Exceptions (`lib/exceptions.py`)

**`MissingConfigError`**: Raised when config file doesn't exist

```python
class MissingConfigError(Exception):
    """Configuration file not found"""
```

**`MissingGranaryError`**: Raised when granary path doesn't exist

```python
class MissingGranaryError(Exception):
    """Granary path does not exist"""
    def __init__(self, path: Path):
        super().__init__(f"Granary path does not exist: {path}")
```

### Traceback Control

Verbosity controls traceback display:

```python
# In lib/cli.py
sys.tracebacklimit = 0  # Default: no tracebacks

if args.verbosity > 0:
    sys.tracebacklimit = 1000  # Full tracebacks
```

## Dependencies

### Core Dependencies

- **dj_settings** (~8.0): Configuration parsing
    - Loads YAML config files
    - Handles hierarchical configuration

- **jinja2** (~3.1): Template rendering
    - Renders templates with variables
    - Uses `StrictUndefined` for safety
    - Preserves trailing newlines

- **pyutilkit** (~0.10): Terminal utilities
    - Colored output (SGR codes)
    - Formatted string printing

- **ruamel.yaml**: YAML handling
    - Reads/writes estate files
    - Preserves formatting

### Why These Choices?

- **dj_settings**: Lightweight, handles nested configs well
- **Jinja2**: Industry-standard templating, powerful features
- **pyutilkit**: Simple terminal formatting without heavy dependencies
- **ruamel.yaml**: Better than PyYAML for round-trip YAML handling

## Testing Strategy

### Test Organization

```
tests/
├── plowman/
│   ├── test_main.py        # Entry point tests
│   └── lib/
│       └── test_cli.py     # CLI parsing tests
```

### Current Coverage

- CLI argument parsing
- Verbosity flag stacking
- Dry-run flag
- Main entry point invocation

### Future Testing Needs

- Command execution logic
- Template rendering
- Estate management
- Hash comparison
- File deployment
- Integration tests

## Performance Considerations

### Optimization Strategies

1. **Hash-based skipping**: Avoids unnecessary file writes
    - SHA256 hashing is fast
    - Only renders templates when needed
    - Significant speedup for re-deployment

2. **Sequential processing**: Simple, predictable memory usage
    - One file at a time
    - No parallel overhead
    - Suitable for typical dotfile counts (<1000 files)

3. **Lazy loading**: Config loaded once, reused
    - Estate loaded at start
    - Templates rendered on-demand

### Potential Improvements

- Parallel file processing for large repositories
- Incremental estate updates
- Caching rendered templates
- Binary diff for large files

## Security Considerations

### Current Safeguards

1. **StrictUndefined**: Prevents silent failures in templates
    - Undefined variables raise errors
    - No accidental empty substitutions

2. **Path validation**: Granary paths must exist
    - Prevents typos in configuration
    - Validates before processing

3. **No arbitrary code execution**: Templates are data-only
    - Jinja2 sandboxed by default
    - No Python code execution in templates

### Areas for Improvement

- Validate template paths don't escape granary
- Sanitize variable values
- Permission checks before writing
- Backup before overwriting (optional feature)

## Extensibility

### Adding New Commands

1. Create new command class inheriting from `BaseCommand`
2. Implement `run()` method
3. Add subparser in `lib/cli.py`
4. Add case in `__main__.py` match statement

Example:

```python
# commands/harvest.py
class HarvestCommand(BaseCommand):
    def run(self) -> None:
        # Implementation
        pass

# lib/cli.py
subparsers.add_parser("harvest", parents=[parent_parser])

# __main__.py
case "harvest":
    HarvestCommand(...).run()
```

### Adding New Features

The modular architecture makes it easy to extend:

- **New config options**: Add to `ParsedConfig` TypedDict
- **New estate features**: Extend `Estate` class
- **New output formats**: Add to `show_diff()` method
- **New template filters**: Configure Jinja2 environment

## Design Decisions

### Why Copy Instead of Symlink?

**Pros of copying:**

- Files are independent after deployment
- Can edit deployed files (though not recommended)
- Works across filesystems
- Simpler mental model

**Cons:**

- Uses more disk space
- Changes must be synced back manually

**Future**: May add symlink mode as option.

### Why SHA256 Hashing?

- Fast enough for typical file sizes
- Cryptographically secure (overkill but safe)
- Standard library support
- Detects any change, no false negatives

### Why YAML for Config?

- Human-readable
- Supports comments
- Hierarchical structure
- Python ecosystem maturity
- Better than JSON for config (comments!)

### Why Not Use Existing Tools?

Existing dotfile managers either:

- Lack template support
- Don't track state
- Are too complex
- Don't have clean abstractions

plowman aims for the sweet spot: powerful but simple.

## Future Directions

### Planned Features

- Multiple config profiles
- Import/export estate files
- Plugin system for custom processors
- Web interface for management
- Sync with remote repositories

### Architectural Improvements

- Async file operations
- Plugin architecture
- Better error recovery
- Comprehensive test coverage
- Performance profiling tools

## Conclusion

plowman's architecture prioritizes simplicity, reliability, and maintainability. The agricultural metaphor provides intuitive naming, while the modular design allows for future extensibility. The current implementation covers the core use case well, with room for growth as the project matures.
