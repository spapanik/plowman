# Installation

This guide covers different methods to install plowman.

## Requirements

- Python >= 3.10 (Python 3.14 preferred)

## Using uv (Recommended)

We recommend using [uv](https://github.com/astral-sh/uv) for installing plowman as it provides an isolated environment for the package, preventing any dependency conflicts.

```console
$ uv tool install --python 3.14 plowman
```

Verify the installation:

```console
$ plm --version
plowman 0.3.1
```

### Why uv?

- Fast package installation and resolution
- Isolated tool environments
- Automatic Python version management
- No dependency conflicts with system packages

## Using pip

You can install plowman using pip if you prefer:

```console
$ pip install plowman
```

Or with a specific Python version:

```console
$ python3.14 -m pip install plowman
```

Verify the installation:

```console
$ plm --version
plowman 0.3.1
```

### Virtual Environment

For better isolation, consider using a virtual environment:

```console
$ python3.14 -m venv ~/.venvs/plowman
$ source ~/.venvs/plowman/bin/activate
$ pip install plowman
```

Add the virtual environment's bin directory to your PATH to use `plm` globally:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.venvs/plowman/bin:$PATH"
```

## From Source

Install directly from the GitHub repository:

```console
$ git clone https://github.com/spapanik/plowman.git
$ cd plowman
$ pip install .
```

This method is useful if you want to:
- Install a specific commit or branch
- Test unreleased features
- Contribute to development

### Install Specific Version

```console
$ git clone https://github.com/spapanik/plowman.git
$ cd plowman
$ git checkout v0.3.1
$ pip install .
```

## Development Installation

If you want to contribute to plowman or modify it, install it in editable mode with development dependencies:

```console
$ git clone https://github.com/spapanik/plowman.git
$ cd plowman
$ pip install -e ".[dev]"
```

This installs:
- plowman in editable mode (changes to source code take effect immediately)
- Testing tools (pytest, pytest-cov)
- Linting tools (ruff, mypy, ty)
- Documentation tools (mkdocs, mkdocs-material)
- Development utilities (ipython, ptpython, ipdb)

### Running Tests

After development installation, run the test suite:

```console
$ pytest
```

Run with coverage:

```console
$ pytest --cov=src/plowman
```

### Code Quality Checks

Run linting:

```console
$ ruff check src/ tests/
$ mypy src/
```

## Platform-Specific Notes

### macOS

On macOS, you may need to install Python first:

```console
$ brew install python@3.14
```

Then install plowman:

```console
$ uv tool install --python 3.14 plowman
```

### Linux

Most Linux distributions include Python. Ensure you have Python 3.10+:

```console
$ python3 --version
Python 3.10.12
```

If your distribution has an older Python, consider using pyenv or installing from source.

### Windows

plowman is designed for Unix-like systems and manages dotfiles in your home directory. While it may work on Windows with WSL (Windows Subsystem for Linux), it's primarily intended for:
- Linux
- macOS
- Other Unix-like systems

## Troubleshooting Installation

### Command Not Found

If `plm` is not found after installation:

**With uv:**
```console
$ which plm
```

If not found, ensure uv's bin directory is in your PATH:
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

**With pip:**
```console
$ which plm
```

Check that the Python bin directory is in your PATH:
```bash
# For user installations
export PATH="$HOME/.local/bin:$PATH"

# For virtual environments
source ~/.venvs/plowman/bin/activate
```

### Permission Errors

If you get permission errors with pip:

```console
$ pip install --user plowman
```

Or use a virtual environment (recommended).

### Python Version Issues

If you get errors about Python version:

```console
$ python3 --version
```

Ensure you have Python 3.10 or higher. If not:

**Using pyenv:**
```console
$ pyenv install 3.14.0
$ pyenv global 3.14.0
```

**Using deadsnakes PPA (Ubuntu):**
```console
$ sudo add-apt-repository ppa:deadsnakes/ppa
$ sudo apt update
$ sudo apt install python3.14
```

### Dependency Conflicts

If you encounter dependency conflicts:

**Use uv (recommended):**
```console
$ uv tool install plowman
```

uv handles dependency isolation automatically.

**Or use a virtual environment:**
```console
$ python3.14 -m venv ~/.venvs/plowman
$ source ~/.venvs/plowman/bin/activate
$ pip install plowman
```

## Next Steps

After installation:

1. Create your configuration: [Configuration Guide](./configuration.md)
2. Follow the tutorial: [Tutorial](./tutorial.md)
3. Read the usage guide: [Usage Guide](./usage/)

Verify your installation works:

```console
$ plm --version
plowman 0.3.1

$ plm sow --help
usage: plm sow [-h] [-v] [-n]
```
