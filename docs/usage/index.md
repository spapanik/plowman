# Usage Guide

This guide explains how to use plowman to manage your dotfiles.

## Introduction

plowman is a command-line tool that deploys configuration files from source directories (granaries) to your home directory. It supports Jinja2 templates for dynamic configuration, tracks deployed files to enable automatic cleanup, and uses smart hashing to skip unchanged files.

## Quick Start

### 1. Configure Granaries

Create or edit `~/.config/plowman/config.yaml`:

```yaml
granaries:
  ~/dotfiles:
    granaries: ["bash", "nvim"]
    variables:
      username: myuser
      hostname: myhost
```

### 2. Add Dotfiles

Place your configuration files in the granary directories:

```
~/dotfiles/
├── bash/
│   ├── .bashrc
│   └── .bash_profile
└── nvim/
    └── init.vim
```

### 3. Deploy

Run the sow command:

```console
$ plm sow
```

This will copy all files from your granaries to the corresponding locations in your home directory.

## CLI Reference

### Main Command

```console
plm sow [OPTIONS]
```

Deploy dotfiles from configured granaries to your home directory.

### Options

- `-v, --verbose`: Increase verbosity level (can be stacked: `-vv`, `-vvv`)
  - Level 1 (`-v`): Show which files are being copied
  - Level 2 (`-vv`): Show file diffs during copy
  - Level 3+ (`-vvv`): Maximum verbosity with full tracebacks on errors
- `-n, --dry-run`: Preview changes without making any modifications
- `-V, --version`: Print version information and exit

### Examples

Basic deployment:
```console
$ plm sow
```

Preview changes first:
```console
$ plm sow --dry-run
```

Verbose output with diffs:
```console
$ plm sow -vv
```

Maximum verbosity for debugging:
```console
$ plm sow -vvv
```

## Workflow Explanation

plowman follows this workflow when you run `plm sow`:

1. **Load Configuration**: Reads `~/.config/plowman/config.yaml`
2. **Parse Granaries**: For each configured path, reads optional `.plowman/plowman.yml` to identify templates
3. **Initialize Estate**: Loads the estate file to track current state
4. **Process Seeds**: For each file in each granary:
   - Determines if it's a template or plain file
   - Calculates the destination path (crop) in your home directory
   - Compares SHA256 hashes to detect changes
   - Renders templates with Jinja2 if needed
   - Writes the file to the destination
   - Shows diff if verbose mode is enabled
5. **Cleanup Orphans**: Removes files tracked in the estate but no longer present in configuration
6. **Update Estate**: Saves the new state to the estate file

## Template Support

plowman uses Jinja2 for template rendering. This allows you to create dynamic configurations with variables.

### Marking Files as Templates

To mark specific files as templates, create a `.plowman/plowman.yml` file in your granary path:

```yaml
# ~/dotfiles/.plowman/plowman.yml
bash:
  templates:
    - .bashrc.j2
    - .bash_profile.j2
```

Files listed here will be processed as Jinja2 templates. All other files are treated as plain files and copied as-is.

### Using Variables

Define variables in your main config:

```yaml
granaries:
  ~/dotfiles:
    granaries: ["bash"]
    variables:
      username: myuser
      hostname: myhost
      email: user@example.com
```

Use them in templates:

```jinja2
# ~/.bashrc.j2
export USER="{{ username }}"
export HOSTNAME="{{ hostname }}"
export EMAIL="{{ email }}"
```

The template will be rendered with the variables substituted:

```bash
# ~/.bashrc
export USER="myuser"
export HOSTNAME="myhost"
export EMAIL="user@example.com"
```

### Template Syntax

Jinja2 provides powerful templating features:

**Variables:**
```jinja2
{{ variable_name }}
```

**Conditionals:**
```jinja2
{% if os == "linux" %}
export SHELL=/bin/bash
{% elif os == "darwin" %}
export SHELL=/bin/zsh
{% endif %}
```

**Loops:**
```jinja2
{% for path in paths %}
export PATH="{{ path }}:$PATH"
{% endfor %}
```

For more Jinja2 features, see the [Jinja2 documentation](https://jinja.palletsprojects.com/).

## Estate Management

### What is the Estate?

The estate is a YAML file that tracks all files deployed by plowman. It's automatically created and maintained at `{path}/.plowman/estate.yml`.

Example estate file:

```yaml
files:
  - .bashrc
  - .bash_profile
  - config:
    - nvim:
      - init.vim
```

### How Estate Tracking Works

1. When plowman deploys a file, it records it in the estate
2. On subsequent runs, plowman compares the estate against current configuration
3. Files in the estate but not in configuration are considered "orphaned" and removed
4. This ensures your home directory stays clean and matches your configuration

### Manual Estate Editing

**Warning**: Do not manually edit the estate file. It's automatically managed by plowman. Manual edits may cause unexpected behavior.

If you need to reset the estate:
1. Delete the estate file: `rm ~/.plowman/estate.yml`
2. Run `plm sow` to rebuild it from scratch

### Dry-Run Mode

Use `--dry-run` to preview what changes would be made without actually making them:

```console
$ plm sow --dry-run
☑️ Would copy /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
☑️ Would copy /home/user/dotfiles/nvim/init.vim to /home/user/.config/nvim/init.vim
🧹 Would delete /home/user/.old_config
```

This is useful for:
- Testing new configurations before applying them
- Understanding what files will be affected
- Verifying cleanup of orphaned files

## Best Practices

### Organizing Granaries

Group related configurations into separate granaries:

```
~/dotfiles/
├── shell/          # Shell configurations
│   ├── .bashrc
│   └── .zshrc
├── editor/         # Editor configurations
│   └── nvim/
│       └── init.vim
└── git/            # Git configurations
    └── .gitconfig
```

### Using Multiple Paths

You can manage multiple independent dotfile repositories:

```yaml
granaries:
  ~/personal-dotfiles:
    granaries: ["shell", "editor"]
    variables:
      type: personal
  
  ~/work-dotfiles:
    granaries: ["git", "ssh"]
    variables:
      type: work
```

### Version Control

Store your granaries in version control (e.g., Git) to:
- Track changes to your configurations
- Sync across multiple machines
- Collaborate with others
- Maintain history

Example `.gitignore` for a dotfiles repository:

```gitignore
# Don't track estate files
.plowman/estate.yml

# Don't track generated files
*.generated
```

### Backup Before Deployment

While plowman overwrites files safely, it's good practice to backup important configurations:

```console
$ cp ~/.bashrc ~/.bashrc.backup
$ plm sow
```

Or use dry-run first to verify changes:

```console
$ plm sow --dry-run -vv
```
