# Configuration Reference

This document explains how to configure plowman using YAML configuration files.

## Overview

plowman uses a hierarchical configuration system with three levels:

1. **Main Config**: `~/.config/plowman/config.yaml` - Defines granaries and variables
2. **Per-Path Config**: `{path}/.plowman/plowman.yml` - Specifies which files are templates
3. **Estate File**: `{path}/.plowman/estate.yml` - Auto-generated state tracking (don't edit manually)

## Main Configuration File

Location: `~/.config/plowman/config.yaml`

This is the primary configuration file where you define your granaries, their locations, and template variables.

### Basic Structure

```yaml
granaries:
  /absolute/path/to/dotfiles:
    granaries:
      - subdir1
      - subdir2
    variables:
      key1: value1
      key2: value2
```

### Fields Explained

#### `granaries` (required)

Top-level mapping of paths to their configurations. Each key is an absolute path to a directory containing your dotfile repositories.

Example:
```yaml
granaries:
  ~/dotfiles:
    # configuration for this path
  ~/work-dotfiles:
    # configuration for another path
```

#### Path Configuration

For each path, you specify:

**`granaries`** (required): List of subdirectories within the path that contain dotfiles.

```yaml
granaries:
  ~/dotfiles:
    granaries:
      - bash
      - nvim
      - git
```

Each listed subdirectory will be scanned recursively for files to deploy.

**`variables`** (optional): Dictionary of variables for Jinja2 template rendering.

```yaml
granaries:
  ~/dotfiles:
    granaries: ["bash", "nvim"]
    variables:
      username: myuser
      hostname: myhost
      email: user@example.com
      os: linux
```

These variables are available in all templates under this path.

### Complete Example

```yaml
granaries:
  ~/personal-dotfiles:
    granaries:
      - shell
      - editor
      - git
    variables:
      username: john
      email: john@example.com
      os: darwin
  
  ~/work-dotfiles:
    granaries:
      - ssh
      - vpn
    variables:
      username: j.doe
      email: john.doe@company.com
      company: acme-corp
```

### Global Options

You can add global options at the top level of the config file:

```yaml
allow_symlinks: false

granaries:
  ~/dotfiles:
    granaries: ["bash"]
```

**`allow_symlinks`** (optional, default: `false`): If set to `true`, plowman will not overwrite symbolic links in the destination. This is useful if you want to manually symlink some files while managing others with plowman.

## Per-Path Configuration

Location: `{path}/.plowman/plowman.yml`

This optional file specifies which files in each granary should be treated as Jinja2 templates. Files not listed here are copied as plain files.

### Structure

```yaml
granary_name:
  name: optional_display_name  # Optional: used for harvest --add-to-estate
  templates:
    - filename.j2
    - another_file.conf.j2
```

The `name` field is optional and provides a human-readable identifier for the granary. This is particularly useful when using the `harvest` command with the `-a/--add-to-estate` option.

### Example

For a path `~/dotfiles` with granaries `bash` and `nvim`:

```yaml
# ~/dotfiles/.plowman/plowman.yml
bash:
  name: myshell  # Optional: use this name with "plm harvest -a myshell::path"
  templates:
    - .bashrc.j2
    - .bash_profile.j2

nvim:
  name: myeditor  # Optional: use this name with "plm harvest -a myeditor::path"
  templates:
    - init.vim.j2
    - coc-settings.json.j2
```

In this example:
- `~/dotfiles/bash/.bashrc.j2` will be rendered as a Jinja2 template
- `~/dotfiles/bash/.bash_profile.j2` will be rendered as a Jinja2 template
- Any other files in `~/dotfiles/bash/` will be copied as-is
- `~/dotfiles/nvim/init.vim.j2` will be rendered as a Jinja2 template
- Other files in `~/dotfiles/nvim/` will be copied as-is

### Template File Naming

While not required, it's common practice to use the `.j2` extension for template files to make them easily identifiable:

```
bash/
├── .bashrc.j2          # Will be rendered as template
├── .bash_aliases       # Will be copied as-is
└── functions.sh        # Will be copied as-is
```

When deployed, the `.j2` extension is removed:
- `.bashrc.j2` → `~/.bashrc`
- `.bash_aliases` → `~/.bash_aliases`

## Estate File

Location: `{path}/.plowman/estate.yml`

The estate file is automatically created and maintained by plowman. It tracks all files that have been deployed to your home directory.

### Purpose

- Tracks which files are managed by plowman
- Enables automatic cleanup of orphaned files
- Prevents accidental deletion of unmanaged files

### Structure

```yaml
files:
  - .bashrc
  - .bash_profile
  - config:
    - nvim:
      - init.vim
  - .gitconfig
```

The structure mirrors the directory hierarchy of deployed files relative to your home directory.

### Important Notes

⚠️ **Do not manually edit the estate file.** It's automatically managed by plowman. Manual edits may cause:
- Orphaned files not being cleaned up
- Files being incorrectly deleted
- State inconsistencies

If you need to reset the estate:
1. Delete the estate file: `rm {path}/.plowman/estate.yml`
2. Run `plm sow` to rebuild it from scratch

## Configuration Examples

### Simple Single Granary

```yaml
granaries:
  ~/dotfiles:
    granaries: ["all"]
```

This deploys everything from `~/dotfiles/all/` to your home directory.

### Multiple Granaries with Variables

```yaml
granaries:
  ~/dotfiles:
    granaries:
      - bash
      - zsh
      - git
    variables:
      username: alice
      email: alice@example.com
      theme: dark
```

### Environment-Specific Configurations

```yaml
granaries:
  ~/dotfiles:
    granaries: ["base"]
    variables:
      environment: development
  
  ~/prod-dotfiles:
    granaries: ["base"]
    variables:
      environment: production
      log_level: warn
```

### Complex Setup with Templates

```yaml
# ~/.config/plowman/config.yaml
granaries:
  ~/dotfiles:
    granaries:
      - shell
      - editor
      - tools
    variables:
      username: bob
      hostname: workstation
      python_version: "3.11"
```

```yaml
# ~/dotfiles/.plowman/plowman.yml
shell:
  templates:
    - .bashrc.j2
    - .zshrc.j2
    - .profile.j2

editor:
  templates:
    - nvim/init.lua.j2
    - nvim/lua/config/keymaps.lua.j2

tools:
  templates: []  # No templates, all files copied as-is
```

## Configuration Best Practices

### Use Absolute Paths

Always use absolute paths in your main config:

```yaml
# Good
granaries:
  /home/user/dotfiles:
    granaries: ["bash"]

# Bad - may not work as expected
granaries:
  ~/dotfiles:
    granaries: ["bash"]
```

Note: The tilde (`~`) expansion works on most systems, but absolute paths are more reliable.

### Organize by Category

Group related configurations into separate granaries:

```
dotfiles/
├── shell/      # Shell configs (.bashrc, .zshrc, etc.)
├── editor/     # Editor configs (nvim, vscode, etc.)
├── git/        # Git configs
├── ssh/        # SSH configs
└── tools/      # Other tool configs
```

### Separate Personal and Work Configs

Use multiple paths for different contexts:

```yaml
granaries:
  ~/personal-dotfiles:
    granaries: ["shell", "editor"]
    variables:
      context: personal
  
  ~/work-dotfiles:
    granaries: ["git", "ssh", "vpn"]
    variables:
      context: work
```

### Version Control Your Config

Store your configuration in version control:

```bash
cd ~/dotfiles
git init
git add .
git commit -m "Initial dotfiles setup"
```

Add estate files to `.gitignore`:

```gitignore
# .gitignore
.plowman/estate.yml
```

### Document Your Variables

Keep track of what variables you use across templates:

```yaml
granaries:
  ~/dotfiles:
    granaries: ["shell"]
    variables:
      # User information
      username: alice
      email: alice@example.com
      
      # System settings
      editor: nvim
      shell: zsh
      
      # Application settings
      theme: dark
      font_size: 14
```

## Troubleshooting Configuration Issues

### MissingConfigError

**Error**: `MissingConfigError: Configuration file not found`

**Solution**: Create `~/.config/plowman/config.yaml` with at least one granary defined.

### MissingGranaryError

**Error**: `MissingGranaryError: Granary path does not exist: /path/to/granary`

**Solution**: 
- Verify the path exists: `ls /path/to/granary`
- Check for typos in the path
- Ensure the path is absolute
- Create the directory if needed: `mkdir -p /path/to/granary`

### Template Rendering Errors

**Error**: Jinja2 undefined variable errors

**Solution**:
- Check that all variables used in templates are defined in config
- Use `--dry-run -vvv` to see detailed error messages
- Verify template syntax is correct

### Invalid YAML

**Error**: YAML parsing errors

**Solution**:
- Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('config.yaml'))"`
- Check indentation (use spaces, not tabs)
- Ensure proper quoting for special characters
