# Frequently Asked Questions (FAQ)

Common questions about using plowman.

## General Questions

### What is plowman?

plowman is a dotfile management tool that uses an agricultural metaphor to deploy configuration files from source directories (granaries) to your home directory. It supports Jinja2 templates, tracks deployed files, and automatically cleans up orphaned configurations.

### Why should I use plowman instead of other dotfile managers?

plowman offers several advantages:

- **Template support**: Built-in Jinja2 templating with variables for dynamic configurations
- **State tracking**: Automatic tracking of deployed files enables smart cleanup
- **Smart updates**: SHA256 hashing skips unchanged files for fast re-deployment
- **Simple configuration**: YAML-based config that's easy to understand
- **Dry-run mode**: Preview changes before applying them
- **Colored diffs**: See exactly what changed with syntax-highlighted output
- **Lightweight**: Minimal dependencies, fast execution

### Is plowman production-ready?

plowman is currently at version 0.3.1, which means it's in early development. While it's functional and stable for basic use cases, the API may change in future versions. It's suitable for personal use but consider testing thoroughly before relying on it for critical systems.

### What platforms does plowman support?

plowman is designed for Unix-like systems:

- Linux (all major distributions)
- macOS
- BSD variants

It may work on Windows with WSL (Windows Subsystem for Linux), but this is not officially supported.

## Configuration Questions

### How do I backup my files before deploying?

plowman doesn't have built-in backup functionality, but you can:

**Manual backup:**

```console
$ cp ~/.bashrc ~/.bashrc.backup
$ plm sow
```

**Use dry-run first:**

```console
$ plm sow --dry-run -vv
```

**Version control your granaries:**

```console
$ cd ~/dotfiles
$ git add .
$ git commit -m "Backup before changes"
```

Since plowman only overwrites files you explicitly configure, unmanaged files are never touched.

### Can I use symlinks instead of copying files?

Currently, plowman copies files rather than creating symlinks. However, you can control symlink behavior:

**Allow symlinks as-is:**

```yaml
# ~/.config/plowman/config.yaml
allow_symlinks: true

estates:
    ~/dotfiles:
        granaries: ["bash"]
```

When `allow_symlinks` is `true`, plowman won't overwrite existing symbolic links in the destination. This lets you manually symlink some files while managing others with plowman.

Future versions may add native symlink support.

### How do I exclude certain files from deployment?

There are several approaches:

**1. Don't include them in granaries:**
Only list subdirectories you want to deploy:

```yaml
estates:
    ~/dotfiles:
        granaries:
            - bash # Deploy this
            # - secrets  # Don't deploy this
```

**2. Use .gitignore patterns:**
If using version control, add sensitive files to `.gitignore`:

```gitignore
# ~/dotfiles/.gitignore
secrets/
*.key
*.pem
```

**3. Separate sensitive configs:**
Keep sensitive files in a separate granary that you don't sync:

```yaml
estates:
    ~/dotfiles:
        granaries: ["bash", "git"]

    # Local-only, not synced
    ~/local-dotfiles:
        granaries: ["secrets"]
```

### What happens if I manually edit a deployed file?

If you manually edit a deployed file (crop), plowman will detect the change on the next run:

- If the source file (seed) hasn't changed, plowman will skip it (hashes match)
- If the source file has changed, plowman will overwrite your manual edits

To preserve manual edits:

1. Copy your changes back to the granary (seed)
2. Or remove the file from your configuration

This is why it's best to edit files in your granaries, not the deployed copies.

### Can I use plowman on multiple machines?

Yes! This is one of plowman's strengths:

**Setup on each machine:**

1. Clone your dotfiles repository
2. Install plowman
3. Create machine-specific config if needed
4. Run `plm sow`

**Handle machine differences:**

Use template variables:

```yaml
# Machine A config
variables:
    hostname: workstation
    os: darwin

# Machine B config
variables:
    hostname: server
    os: linux
```

Or use conditionals in templates:

```jinja2
{% if hostname == "workstation" %}
export DISPLAY=:0
{% endif %}
```

You can also maintain separate granaries per machine type.

## Template Questions

### How do I debug template rendering errors?

Use maximum verbosity to see detailed error messages:

```console
$ plm sow --dry-run -vvv
```

Common issues:

- **Undefined variable**: Check that all variables used in templates are defined in config
- **Syntax error**: Verify Jinja2 syntax is correct
- **Missing file**: Ensure template file exists in the granary

Example error:

```
jinja2.exceptions.UndefinedError: 'username' is undefined
```

Fix by adding the variable to your config:

```yaml
variables:
    username: alice
```

### Can I use complex Jinja2 features?

Yes! plowman uses the full Jinja2 engine, so you can use:

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

**Filters:**

```jinja2
{{ username | upper }}
{{ email | default("user@example.com") }}
```

**Macros:**

```jinja2
{% macro set_env(name, value) %}
export {{ name }}="{{ value }}"
{% endmacro %}

{{ set_env("EDITOR", editor) }}
```

See the [Jinja2 documentation](https://jinja.palletsprojects.com/) for complete reference.

### How do I escape Jinja2 syntax in plain files?

If a file contains `{{` or `{%` but shouldn't be processed as a template, either:

**1. Don't mark it as a template:**
Only list actual templates in `.plowman/plowman.yml`

**2. Use raw blocks:**

```jinja2
{% raw %}
This won't be processed: {{ variable }}
{% endraw %}
```

## Estate Questions

### What is the estate file and do I need to worry about it?

The estate file (`{path}/.plowman/estate.yml`) automatically tracks which files plowman has deployed. You generally don't need to interact with it directly.

**What it does:**

- Records deployed files for cleanup
- Enables automatic removal of orphaned files
- Maintains state between runs

**Don't edit it manually** - it's auto-generated and managed by plowman.

### How do I reset the estate file?

If the estate file gets corrupted or out of sync:

```console
# Delete the estate file
$ rm ~/dotfiles/.plowman/estate.yml

# Rebuild from scratch
$ plm sow
```

This will redeploy all files and create a fresh estate file.

### Can I share estate files between machines?

No, estate files are machine-specific because:

- They track files relative to your home directory
- Different machines may have different files deployed
- They're auto-generated based on actual deployments

Each machine should maintain its own estate file.

## Troubleshooting Questions

### Why aren't my changes being applied?

Check these common issues:

**1. File hasn't changed (hash match):**
plowman skips unchanged files. Force re-deployment by:

- Touching the source file: `touch ~/dotfiles/bash/.bashrc`
- Or deleting the estate file and re-running

**2. Wrong granary path:**
Verify the path in your config matches the actual location:

```console
$ ls ~/dotfiles/bash/.bashrc
```

**3. Template not marked:**
Ensure the file is listed in `.plowman/plowman.yml` if it's a template

**4. Verbose output:**
Run with `-v` to see what's happening:

```console
$ plm sow -v
```

### Why are files being deleted?

Files are deleted when they're:

- In the estate file (previously deployed)
- No longer in your current configuration

This is intentional cleanup. To prevent deletion:

- Add the file back to your granaries
- Or remove it from the estate file (by resetting estate)

Use dry-run to preview deletions:

```console
$ plm sow --dry-run -v
🧹 Would delete /home/user/.old_file
```

### How do I see what files plowman manages?

Check the estate file:

```console
$ cat ~/dotfiles/.plowman/estate.yml
files:
  - .bashrc
  - .gitconfig
  - config:
    - nvim:
      - init.vim
```

Or use verbose mode during deployment:

```console
$ plm sow -v
☑️ Copying /source to /destination
```

## Migration Questions

### How do I migrate from another dotfile manager?

General steps:

**1. Organize your existing dotfiles:**

```console
$ mkdir -p ~/dotfiles/{bash,git,nvim}
$ mv ~/.bashrc ~/dotfiles/bash/
$ mv ~/.gitconfig ~/dotfiles/git/
```

**2. Create plowman config:**

```yaml
estates:
    ~/dotfiles:
        granaries:
            - bash
            - git
            - nvim
```

**3. Test with dry-run:**

```console
$ plm sow --dry-run -v
```

**4. Deploy:**

```console
$ plm sow
```

**5. Clean up old manager:**
Remove the old dotfile manager once you've verified everything works.

### Can I gradually migrate to plowman?

Yes! Start small:

**Phase 1:** Manage just one granary

```yaml
estates:
    ~/dotfiles:
        granaries: ["bash"] # Start with just bash
```

**Phase 2:** Add more granaries as you're comfortable

```yaml
estates:
    ~/dotfiles:
        granaries:
            - bash
            - git # Added
```

**Phase 3:** Add templates and variables

```yaml
estates:
    ~/dotfiles:
        granaries: ["bash", "git"]
        variables: # Added
            username: alice
```

This gradual approach lets you test and verify each step.

## Performance Questions

### How fast is plowman?

plowman is very fast because:

- It uses SHA256 hashing to skip unchanged files
- Only modified files are actually written
- Templates are only rendered when needed

For typical dotfile setups (<100 files), deployment takes <1 second.

### Does plowman use a lot of memory?

No, plowman is lightweight:

- Processes files one at a time
- Doesn't load entire files into memory unnecessarily
- Minimal dependencies

Memory usage is typically <50MB even for large dotfile repositories.

## Still Have Questions?

If your question isn't answered here:

- Check the [Usage Guide](./usage/) for detailed instructions
- Read the [Configuration Reference](./configuration.md) for config options
- See [Troubleshooting](./troubleshooting.md) for common issues
- Open an issue on [GitHub](https://github.com/spapanik/plowman/issues)
