# CLI Reference

Complete reference for plowman command-line interface.

## Overview

plowman provides a single command `plm` with one subcommand `sow` for deploying dotfiles.

## Command Structure

```console
plm [GLOBAL_OPTIONS] <SUBCOMMAND> [SUBCOMMAND_OPTIONS]
```

## Global Options

These options apply to all commands:

### `-V, --version`

Print version information and exit.

```console
$ plm --version
plowman 0.3.1
```

### `-h, --help`

Show help message and exit.

```console
$ plm --help
usage: plm [-h] [-V] {sow} ...

Dotfile farm manager

positional arguments:
  {sow}
    sow         Deploy dotfiles

options:
  -h, --help    show this help message and exit
  -V, --version print the version and exit
```

## Subcommands

### `sow`

Deploy dotfiles from configured granaries to your home directory.

#### Synopsis

```console
plm sow [OPTIONS]
```

#### Description

The `sow` command reads your configuration from `~/.config/plowman/config.yaml`, processes all configured granaries, and deploys files to your home directory. It:

- Renders Jinja2 templates with configured variables
- Tracks deployed files in estate files
- Skips unchanged files using SHA256 hashing
- Removes orphaned files no longer in configuration
- Shows colored diffs in verbose mode

#### Options

##### `-v, --verbose`

Increase verbosity level. Can be stacked multiple times.

**Level 0 (default):** Minimal output, only errors shown

```console
$ plm sow
(no output if no changes)
```

**Level 1 (`-v`):** Show which files are being copied

```console
$ plm sow -v
☑️ Copying /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
☑️ Copying /home/user/dotfiles/git/.gitconfig to /home/user/.gitconfig
```

**Level 2 (`-vv`):** Show file diffs during copy

```console
$ plm sow -vv
☑️ Copying /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
    @@ -1,5 +1,5 @@
     # My bash configuration
     
     # Aliases
    -alias ll='ls -l'
    +alias ll='ls -la'
     alias gs='git status'
```

**Level 3+ (`-vvv`):** Maximum verbosity with full tracebacks on errors

```console
$ plm sow -vvv
☑️ Copying /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
    @@ -1,5 +1,5 @@
     # My bash configuration
    ...
```

When verbosity is enabled, Python tracebacks will show full stack traces for debugging.

##### `-n, --dry-run`

Perform a trial run without making any changes to the filesystem.

```console
$ plm sow --dry-run
☑️ Would copy /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
☑️ Would copy /home/user/dotfiles/git/.gitconfig to /home/user/.gitconfig
🧹 Would delete /home/user/.old_config
```

Useful for:
- Previewing changes before applying them
- Testing new configurations
- Verifying cleanup of orphaned files
- Understanding what will be affected

Can be combined with verbose flags:

```console
$ plm sow --dry-run -vv
☑️ Would copy /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
    @@ -1,5 +1,5 @@
     # My bash configuration
    -alias ll='ls -l'
    +alias ll='ls -la'
```

##### `-h, --help`

Show help for the sow command.

```console
$ plm sow --help
usage: plm sow [-h] [-v] [-n]

options:
  -h, --help     show this help message and exit
  -v, --verbose  increase the level of verbosity
  -n, --dry-run  perform a trial run with no changes made
```

## Output Format

### Success Messages

Files being copied:
```
☑️ Copying /source/path to /destination/path
```

Files that would be copied (dry-run):
```
☑️ Would copy /source/path to /destination/path
```

Files being deleted (orphaned):
```
🧹 Deleting /path/to/orphaned/file
```

Files that would be deleted (dry-run):
```
🧹 Would delete /path/to/orphaned/file
```

### Diff Output

Diffs use unified diff format with color coding:

- **Cyan**: Hunk headers (`@@ -1,5 +1,5 @@`)
- **Yellow/Bold**: File paths (`--- old`, `+++ new`)
- **Green**: Added lines (`+new content`)
- **Red**: Removed lines (`-old content`)
- **Default**: Context lines (unchanged)

Example:
```
    @@ -1,5 +1,5 @@
     # My bash configuration
     
     # Aliases
    -alias ll='ls -l'
    +alias ll='ls -la'
     alias gs='git status'
```

### Error Messages

Errors are printed to stderr with red coloring when available.

## Exit Codes

- **0**: Success - operation completed successfully
- **1**: Error - operation failed (see error message for details)

Common error scenarios:
- Missing configuration file
- Missing granary directory
- Template rendering errors
- Permission denied

## Environment Variables

plowman does not currently use any environment variables for configuration. All settings are controlled via configuration files and command-line flags.

## Configuration Files

While not command-line options, these files affect plowman's behavior:

### Main Config
- **Location**: `~/.config/plowman/config.yaml`
- **Purpose**: Defines granaries, paths, and variables
- **Required**: Yes

### Per-Path Config
- **Location**: `{path}/.plowman/plowman.yml`
- **Purpose**: Specifies which files are templates
- **Required**: No (optional)

### Estate File
- **Location**: `{path}/.plowman/estate.yml`
- **Purpose**: Tracks deployed files for cleanup
- **Required**: Auto-generated (don't edit manually)

## Examples

### Basic deployment
```console
$ plm sow
```

### Preview changes
```console
$ plm sow --dry-run
```

### Verbose deployment
```console
$ plm sow -v
```

### Verbose with diffs
```console
$ plm sow -vv
```

### Maximum verbosity for debugging
```console
$ plm sow -vvv
```

### Dry-run with verbose output
```console
$ plm sow --dry-run -vv
```

### Check version
```console
$ plm --version
plowman 0.3.1
```

### Get help
```console
$ plm --help
$ plm sow --help
```

## Tips

### Combining Flags

Flags can be combined in various ways:

```console
# These are equivalent
$ plm sow -vvv
$ plm sow -v -v -v
$ plm sow --verbose --verbose --verbose

# Dry-run with verbosity
$ plm sow -n -vv
$ plm sow --dry-run -vv
```

### Quick Verification

After making changes to your granaries:

```console
# Quick check of what changed
$ plm sow --dry-run -v

# See detailed diffs
$ plm sow --dry-run -vv

# Apply if satisfied
$ plm sow
```

### Debugging Issues

If something goes wrong:

```console
# Maximum verbosity shows full tracebacks
$ plm sow -vvv

# Or combine with dry-run to see issues without making changes
$ plm sow --dry-run -vvv
```

### Silent Operation

For scripts or cron jobs where you don't want output:

```console
# Only errors will be shown
$ plm sow 2>/dev/null

# Or redirect all output
$ plm sow >/dev/null 2>&1
```

Note: plowman doesn't have a quiet flag, so use shell redirection if needed.
