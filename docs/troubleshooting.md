# Troubleshooting Guide

Common issues and their solutions when using plowman.

## Installation Issues

### Command Not Found

**Problem:** After installation, `plm` command is not found.

```console
$ plm --version
command not found: plm
```

**Solutions:**

**If installed with uv:**
```console
# Check if uv's bin directory is in PATH
$ which plm

# Add to shell config (~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
$ source ~/.bashrc
```

**If installed with pip:**
```console
# Check Python's bin directory
$ python3 -m site --user-base
/home/user/.local

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Or use virtual environment
$ source ~/.venvs/plowman/bin/activate
```

**Verify installation:**
```console
$ which plm
/home/user/.local/bin/plm

$ plm --version
plowman 0.3.1
```

### Permission Errors

**Problem:** Permission denied when installing with pip.

```console
$ pip install plowman
PermissionError: [Errno 13] Permission denied: '/usr/lib/python3.10'
```

**Solutions:**

**Use --user flag:**
```console
$ pip install --user plowman
```

**Use virtual environment (recommended):**
```console
$ python3 -m venv ~/.venvs/plowman
$ source ~/.venvs/plowman/bin/activate
$ pip install plowman
```

**Use uv (best option):**
```console
$ uv tool install plowman
```

uv handles isolation automatically and doesn't require sudo.

### Python Version Issues

**Problem:** Error about Python version requirements.

```console
ERROR: Package 'plowman' requires a different Python: 3.9.0 not in '>=3.10'
```

**Solutions:**

**Check current Python version:**
```console
$ python3 --version
Python 3.9.0
```

**Install newer Python:**

On macOS with Homebrew:
```console
$ brew install python@3.14
```

On Ubuntu/Debian:
```console
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt update
$ sudo apt install python3.14
```

Using pyenv:
```console
$ pyenv install 3.14.0
$ pyenv global 3.14.0
```

**Then reinstall plowman:**
```console
$ pip uninstall plowman
$ pip install plowman
```

## Configuration Issues

### MissingConfigError

**Problem:** Configuration file not found.

```console
plowman.lib.exceptions.MissingConfigError: Configuration file not found at ~/.config/plowman/config.yaml
```

**Solution:**

Create the configuration file:
```console
$ mkdir -p ~/.config/plowman
$ cat > ~/.config/plowman/config.yaml << 'EOF'
estates:
  ~/dotfiles:
    granaries: ["bash"]
EOF
```

Verify it exists:
```console
$ ls -la ~/.config/plowman/config.yaml
-rw-r--r-- 1 user user 50 Jun 24 10:00 /home/user/.config/plowman/config.yaml
```

### MissingGranaryError

**Problem:** Granary directory doesn't exist.

```console
plowman.lib.exceptions.MissingGranaryError: Granary path does not exist: /home/user/dotfiles/bash
```

**Solutions:**

**Check the path:**
```console
$ ls ~/dotfiles/bash
ls: cannot access '/home/user/dotfiles/bash': No such file or directory
```

**Create the directory:**
```console
$ mkdir -p ~/dotfiles/bash
```

**Fix typo in config:**
```yaml
# Wrong
estates:
  ~/dotfiles:
    granaries: ["bsh"]  # Typo!

# Correct
estates:
  ~/dotfiles:
    granaries: ["bash"]
```

**Use absolute paths:**
```yaml
# Better
estates:
  /home/user/dotfiles:
    granaries: ["bash"]
```

### Invalid YAML Syntax

**Problem:** YAML parsing errors.

```console
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Solutions:**

**Validate YAML syntax:**
```console
$ python3 -c "import yaml; yaml.safe_load(open('~/.config/plowman/config.yaml'))"
```

**Common issues:**

Tabs instead of spaces:
```yaml
# Wrong (uses tabs)
estates:
→~/dotfiles:
→→granaries: ["bash"]

# Correct (uses spaces)
estates:
  ~/dotfiles:
    granaries: ["bash"]
```

Missing quotes for special characters:
```yaml
# Wrong
variables:
  email: user@example.com

# Correct
variables:
  email: "user@example.com"
```

Incorrect indentation:
```yaml
# Wrong
estates:
~/dotfiles:
granaries: ["bash"]

# Correct
estates:
  ~/dotfiles:
    granaries: ["bash"]
```

## Template Issues

### Undefined Variable Error

**Problem:** Jinja2 can't find a variable.

```console
jinja2.exceptions.UndefinedError: 'username' is undefined
```

**Solutions:**

**Add variable to config:**
```yaml
estates:
  ~/dotfiles:
    granaries: ["bash"]
    variables:
      username: alice  # Add this
```

**Check template syntax:**
```jinja2
# Wrong
{{ usernmae }}  # Typo!

# Correct
{{ username }}
```

**Use default filter:**
```jinja2
{{ username | default("anonymous") }}
```

**Debug with verbose mode:**
```console
$ plm sow --dry-run -vvv
```

### Template Syntax Error

**Problem:** Jinja2 syntax error in template.

```console
jinja2.exceptions.TemplateSyntaxError: unexpected char '%' at position 10
```

**Solutions:**

**Check for typos:**
```jinja2
# Wrong
{% if os == "linux" %
{% endif %}

# Correct
{% if os == "linux" %}
{% endif %}
```

**Balance blocks:**
```jinja2
# Wrong
{% if condition %}
content
# Missing endif

# Correct
{% if condition %}
content
{% endif %}
```

**Escape literal braces:**
```jinja2
# If you need literal {{ in output
{% raw %}
{{ this won't be processed }}
{% endraw %}
```

### Template Not Being Rendered

**Problem:** Template file is copied as-is without variable substitution.

**Solutions:**

**Mark file as template:**
```yaml
# ~/dotfiles/.plowman/plowman.yml
bash:
  templates:
    - .bashrc.j2  # Must be listed here
```

**Check file extension:**
Template files commonly use `.j2` extension, but any extension works as long as it's listed in the templates config.

**Verify template is in correct granary:**
```console
$ ls ~/dotfiles/bash/.bashrc.j2
/home/user/dotfiles/bash/.bashrc.j2

# Check config matches
$ cat ~/dotfiles/.plowman/plowman.yml
bash:
  templates:
    - .bashrc.j2
```

## Deployment Issues

### Files Not Being Deployed

**Problem:** Expected files are not deployed to home directory.

**Solutions:**

**Check granary configuration:**
```yaml
estates:
  ~/dotfiles:
    granaries:
      - bash      # Is this listed?
      - nvim
```

**Verify files exist in granary:**
```console
$ ls ~/dotfiles/bash/
.bashrc
.bash_profile
```

**Run with verbose output:**
```console
$ plm sow -v
☑️ Copying /home/user/dotfiles/bash/.bashrc to /home/user/.bashrc
```

**Check for hash match (file unchanged):**
If the file hasn't changed since last deployment, plowman skips it. Force re-deployment:
```console
$ touch ~/dotfiles/bash/.bashrc
$ plm sow -v
```

### Files Being Deleted Unexpectedly

**Problem:** Files are removed that you didn't expect.

**Cause:** Files tracked in estate but no longer in configuration are considered orphaned and deleted.

**Solutions:**

**Preview deletions first:**
```console
$ plm sow --dry-run -v
🧹 Would delete /home/user/.old_config
```

**Add file back to configuration:**
```yaml
estates:
  ~/dotfiles:
    granaries:
      - bash
      - old_config  # Re-add this
```

**Reset estate if needed:**
```console
$ rm ~/dotfiles/.plowman/estate.yml
$ plm sow
```

### Permission Denied on Write

**Problem:** Can't write to destination.

```console
PermissionError: [Errno 13] Permission denied: '/home/user/.bashrc'
```

**Solutions:**

**Check file permissions:**
```console
$ ls -la ~/.bashrc
-rw------- 1 root root 123 Jun 24 10:00 /home/user/.bashrc
```

**Fix ownership:**
```console
$ sudo chown $USER:$USER ~/.bashrc
```

**Or run as correct user:**
Don't use sudo with plowman. It should run as your user.

## Estate Issues

### Estate File Corruption

**Problem:** Estate file is malformed or causes errors.

```console
yaml.parser.ParserError: while parsing a block mapping
```

**Solution:**

Delete and rebuild:
```console
$ rm ~/dotfiles/.plowman/estate.yml
$ plm sow
```

This creates a fresh estate file from scratch.

### Estate Out of Sync

**Problem:** Estate doesn't match actual deployed files.

**Symptoms:**
- Files being deleted that shouldn't be
- Files not being cleaned up that should be

**Solution:**

Reset estate:
```console
$ rm ~/dotfiles/.plowman/estate.yml
$ plm sow -v
```

Verify all expected files are deployed:
```console
$ cat ~/dotfiles/.plowman/estate.yml
```

## Performance Issues

### Slow Deployment

**Problem:** plowman takes a long time to deploy.

**Causes and Solutions:**

**Many files:**
plowman processes files sequentially. For hundreds of files, this may take time.

**Network filesystems:**
If granaries are on NFS or similar, file operations are slower.

**Solution - Use hashing efficiently:**
plowman already skips unchanged files via SHA256 hashing. Ensure you're not forcing re-deployment unnecessarily.

**Debug slow runs:**
```console
$ time plm sow -v
```

### High Memory Usage

**Problem:** plowman uses more memory than expected.

**Note:** This is unlikely as plowman is designed to be lightweight. If you experience this:

**Check for very large files:**
Templates are loaded into memory for rendering.

**Solution:**
Split large configurations into multiple smaller granaries.

## Debugging Tips

### Enable Maximum Verbosity

For detailed debugging output:

```console
$ plm sow -vvv
```

This shows:
- All files being processed
- Full diffs for changes
- Complete tracebacks on errors

### Use Dry-Run for Safe Testing

Always test changes with dry-run first:

```console
$ plm sow --dry-run -vv
```

This shows what would happen without making changes.

### Check Configuration Files

Validate your configuration:

```console
# Main config
$ cat ~/.config/plowman/config.yaml

# Per-path config
$ cat ~/dotfiles/.plowman/plowman.yml

# Estate file
$ cat ~/dotfiles/.plowman/estate.yml
```

### Verify File Paths

Ensure paths are correct:

```console
# Check granary exists
$ ls ~/dotfiles/bash/

# Check config path
$ ls ~/.config/plowman/config.yaml

# Check template markers
$ ls ~/dotfiles/.plowman/plowman.yml
```

### Test Template Rendering

Test a template manually:

```console
$ python3 << 'EOF'
from jinja2 import Template

template = Template(open("~/dotfiles/bash/.bashrc.j2").read())
result = template.render(username="alice", hostname="workstation")
print(result)
EOF
```

## Getting Help

If you're still stuck:

1. **Check the docs:**
   - [Usage Guide](./usage/)
   - [Configuration Reference](./configuration.md)
   - [FAQ](./faq.md)

2. **Search existing issues:**
   [GitHub Issues](https://github.com/spapanik/plowman/issues)

3. **Open a new issue:**
   Include:
   - plowman version: `plm --version`
   - Error message (full traceback with `-vvv`)
   - Relevant config snippets
   - What you expected vs what happened

4. **Community:**
   Check if there's a community forum or chat for plowman users.
