# CLI Reference

Complete reference for plowman command-line interface.

## Overview

plowman provides a single command `plm` with two subcommands:
- **`sow`**: Deploy dotfiles from granaries to your home directory
- **`harvest`**: Collect changes from your home directory back to granaries

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
usage: plm [-h] [-V] {sow,harvest} ...

Dotfile farm manager

positional arguments:
  {sow,harvest}
    sow         Deploy dotfiles
    harvest     Collect changes back to granaries

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

### `harvest`

Collect changed files from your home directory back into granaries. This is the opposite of `sow`.

#### Synopsis

```console
plm harvest [OPTIONS] [-a GRANARY::PATH ...]
```

#### Description

The `harvest` command reads your configuration and estate files, detects which managed files have been modified in your home directory, and copies them back to their respective granaries. It:

- Compares files in HOME with versions in granaries using SHA256 hashing
- Copies only changed files back to granaries
- Supports adding new files to estate tracking via `-a/--add-to-estate`
- Handles template files (preserves `.j2` suffix in granaries)
- Updates estate files to reflect current state
- Shows colored diffs in verbose mode

**Use cases:**
- You manually edited a config file in HOME and want to sync it back to your dotfiles repo
- You want to backup changes made on one machine to your central dotfiles repository
- You're migrating configs and need to collect all changes

#### Options

##### `-v, --verbose`

Increase verbosity level. Can be stacked multiple times.

**Level 0 (default):** Minimal output, only errors shown

```console
$ plm harvest
(no output if no changes)
```

**Level 1 (`-v`):** Show which files are being harvested

```console
$ plm harvest -v
☑️ Harvesting /home/user/.bashrc to /home/user/dotfiles/bash/.bashrc
☑️ Harvesting /home/user/.gitconfig to /home/user/dotfiles/git/.gitconfig.j2
```

**Level 2 (`-vv`):** Show file diffs during harvest

```console
$ plm harvest -vv
☑️ Harvesting /home/user/.bashrc to /home/user/dotfiles/bash/.bashrc
    @@ -1,5 +1,5 @@
     # My bash configuration
     
     # Aliases
    -alias ll='ls -l'
    +alias ll='ls -la'
     alias gs='git status'
```

**Level 3+ (`-vvv`):** Maximum verbosity with full tracebacks on errors

When verbosity is enabled, Python tracebacks will show full stack traces for debugging.

##### `-n, --dry-run`

Perform a trial run without making any changes to the filesystem.

```console
$ plm harvest --dry-run
☑️ Would harvest /home/user/.bashrc to /home/user/dotfiles/bash/.bashrc
☑️ Would harvest /home/user/.gitconfig to /home/user/dotfiles/git/.gitconfig.j2
```

Useful for:
- Previewing what would be collected
- Testing before committing changes to your dotfiles repo
- Understanding which files have diverged

Can be combined with verbose flags:

```console
$ plm harvest --dry-run -vv
☑️ Would harvest /home/user/.bashrc to /home/user/dotfiles/bash/.bashrc
    @@ -1,5 +1,5 @@
     # My bash configuration
    -alias ll='ls -l'
    +alias ll='ls -la'
```

##### `-a, --add-to-estate`

Copy new files into a granary. Format: `granary_name::path`

```console
$ plm harvest -a mydots::/home/user/.newconfig
☑️ Harvesting /home/user/.newconfig to /home/user/dotfiles/mydots/.newconfig
```

This option:
- Immediately copies the file to the named granary
- Leaves estate tracking unchanged; the next `sow` tracks the new granary file normally
- Requires the granary to have a `name` field in its `.plowman/plowman.yml` config
- Can specify multiple paths: `-a name1::/path1 name2::/path2`

**Example with multiple paths:**

```console
$ plm harvest -a shell::/home/user/.zshrc shell::/home/user/.zprofile
☑️ Harvesting /home/user/.zshrc to /home/user/dotfiles/shell/.zshrc
☑️ Harvesting /home/user/.zprofile to /home/user/dotfiles/shell/.zprofile
```

**Error handling:**

If the granary name doesn't exist:
```console
$ plm harvest -a nonexistent::/home/user/.file
Error: Granary name 'nonexistent' not found. Available names: shell, editor, git
```

If format is invalid:
```console
$ plm harvest -a /home/user/.file
Error: Invalid format for --add-to-estate: '/home/user/.file'. Expected format: granary_name::path
```

##### `-h, --help`

Show help for the harvest command.

```console
$ plm harvest --help
usage: plm harvest [-h] [-v] [-n] [-a [ADD_TO_ESTATE ...]]

options:
  -h, --help            show this help message and exit
  -v, --verbose         increase the level of verbosity
  -n, --dry-run         perform a trial run with no changes made
  -a, --add-to-estate   paths to add to estate and harvest (format: name::path)
```

## Output Format

### Success Messages

Files being harvested:
```
☑️ Harvesting /source/path to /destination/path
```

Files that would be harvested (dry-run):
```
☑️ Would harvest /source/path to /destination/path
```

### Diff Output

Diffs use unified diff format with color coding:

- **Cyan**: Hunk headers (`@@ -1,5 +1,5 @@`)
- **Yellow/Bold**: File paths (`--- old`, `+++ new`)
- **Green**: Added lines in crop (`+new content`)
- **Red**: Removed lines from seed (`-old content`)
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

Note: For harvest, the "old" version is from the granary (seed) and the "new" version is from HOME (crop).

### Error Messages

Errors are printed to stderr with red coloring when available.

Common errors:
- Invalid `--add-to-estate` format
- Granary name not found
- Permission denied when writing to granary
- File doesn't exist in HOME

## Exit Codes

- **0**: Success - operation completed successfully
- **1**: Error - operation failed (see error message for details)

Common error scenarios:
- Missing configuration file
- Invalid `--add-to-estate` format
- Granary name not found
- Permission denied
- Template rendering errors (shouldn't occur in harvest, but possible)

## Configuration Requirements for Harvest

### Granary Naming

To use `-a/--add-to-estate`, granaries must have a `name` field in their per-path config:

```yaml
# ~/dotfiles/.plowman/plowman.yml
shell:
  name: myshell  # This name is used with --add-to-estate
  templates:
    - .bashrc.j2
    - .zshrc.j2

editor:
  name: myeditor
  templates:
    - init.vim.j2
```

Then use the name with harvest:
```console
$ plm harvest -a myshell::/home/user/.newconfig
```

## Examples

### Basic harvest
```console
$ plm harvest
```

### Preview changes
```console
$ plm harvest --dry-run
```

### Verbose harvest
```console
$ plm harvest -v
```

### Verbose with diffs
```console
$ plm harvest -vv
```

### Dry-run with verbose output
```console
$ plm harvest --dry-run -vv
```

### Add new file to estate and harvest
```console
$ plm harvest -a myshell::/home/user/.tmux.conf
```

### Add multiple files
```console
$ plm harvest -a myshell::/home/user/.tmux.conf myshell::/home/user/.screenrc
```

### Harvest with maximum verbosity for debugging
```console
$ plm harvest -vvv
```

## Tips

### Workflow: Edit → Harvest → Commit

Typical workflow when you make manual changes:

```console
# 1. Edit a config file directly in HOME
$ nvim ~/.bashrc

# 2. Preview what changed
$ plm harvest --dry-run -vv

# 3. Harvest the changes back to granary
$ plm harvest -v

# 4. Review and commit to your dotfiles repo
$ cd ~/dotfiles
$ git status
$ git add bash/.bashrc
$ git commit -m "Update bashrc with new aliases"
$ git push
```

### Sync Across Machines

Harvest changes on one machine, then sow on another:

```console
# On Machine A (where you made changes)
$ plm harvest -v

# Commit and push to Git
$ cd ~/dotfiles
$ git add .
$ git commit -m "Sync changes from Machine A"
$ git push

# On Machine B
$ cd ~/dotfiles
$ git pull
$ plm sow -v
```

### Combining Flags

Flags can be combined in various ways:

```console
# These are equivalent
$ plm harvest -vvv
$ plm harvest -v -v -v
$ plm harvest --verbose --verbose --verbose

# Dry-run with verbosity
$ plm harvest -n -vv
$ plm harvest --dry-run -vv

# Add to estate with verbosity
$ plm harvest -a myshell::/path -v
```

### Quick Verification

After editing configs in HOME:

```console
# Quick check of what changed
$ plm harvest --dry-run -v

# See detailed diffs
$ plm harvest --dry-run -vv

# Harvest if satisfied
$ plm harvest
```

### Debugging Issues

If something goes wrong:

```console
# Maximum verbosity shows full tracebacks
$ plm harvest -vvv

# Or combine with dry-run to see issues without making changes
$ plm harvest --dry-run -vvv
```

### Silent Operation

For scripts or cron jobs:

```console
# Only errors will be shown
$ plm harvest 2>/dev/null

# Or redirect all output
$ plm harvest >/dev/null 2>&1
```

### Template Files

When harvesting template files:
- The file in HOME has no `.j2` extension (e.g., `.bashrc`)
- The file in granary has `.j2` extension (e.g., `.bashrc.j2`)
- Harvest automatically handles this mapping
- The harvested file preserves the `.j2` extension in the granary

```console
# HOME has: ~/.bashrc (rendered, no .j2)
# Granary has: ~/dotfiles/bash/.bashrc.j2 (template)

$ plm harvest -v
☑️ Harvesting /home/user/.bashrc to /home/user/dotfiles/bash/.bashrc.j2
```

## Troubleshooting

### "Granary name not found" Error

Make sure the granary has a `name` field in `.plowman/plowman.yml`:

```yaml
# Check this file exists and has a name
cat ~/dotfiles/.plowman/plowman.yml
```

### No Changes Detected

Harvest only collects files that differ between HOME and granary. If files are identical, nothing happens. Use `--dry-run -vv` to verify.

### Permission Denied

Ensure you have write access to the granary directories:

```console
$ ls -la ~/dotfiles/
```

Fix permissions if needed:

```console
$ chmod -R u+w ~/dotfiles/
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
