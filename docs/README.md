# plowman: Dotfile farm manager

[![build][build_badge]][build_url]
[![lint][lint_badge]][lint_url]
[![tests][tests_badge]][tests_url]
[![license][licence_badge]][licence_url]
[![codecov][codecov_badge]][codecov_url]
[![readthedocs][readthedocs_badge]][readthedocs_url]
[![pypi][pypi_badge]][pypi_url]
[![downloads][pepy_badge]][pepy_url]

**plowman** is a dotfile management tool that uses an agricultural metaphor to manage your configuration files. It deploys dotfiles from central repositories (called "granaries") to your home directory (where they become "crops"), tracking them in an "estate" file to manage their lifecycle.

## Features

- **Template rendering**: Use Jinja2 templates with custom variables for dynamic configurations
- **State tracking**: Automatically track which files are managed via estate files  
- **Smart updates**: Skip unchanged files using SHA256 hashing for efficient deployments
- **Automatic cleanup**: Remove orphaned files that are no longer in your configuration
- **Dry-run mode**: Preview changes before applying them with `--dry-run`
- **Colored diffs**: See exactly what changed with syntax-highlighted diff output
- **Multiple granaries**: Manage dotfiles from multiple source directories with different variables

## Quick Start

Install plowman using uv:

```console
$ uv tool install plowman
```

Create a basic configuration at `~/.config/plowman/config.yaml`:

```yaml
granaries:
  ~/dotfiles:
    granaries: ["bash", "nvim"]
    variables:
      username: myuser
      hostname: myhost
```

Deploy your dotfiles:

```console
$ plm sow
```

## The Agricultural Metaphor

plowman uses an agricultural metaphor for managing dotfiles:

- **Granaries**: Source directories containing your dotfile templates and files
- **Seeds**: Individual source files in granaries (templates or plain files)  
- **Crops**: Deployed files in your home directory
- **Estate**: State tracking file that records which crops are managed

This metaphor represents the process of planting (deploying) configuration files from source granaries to your home directory, where they grow into usable configuration files.

## Next Steps

- [Installation Guide](./installation.md) - How to install plowman
- [Tutorial](./tutorial.md) - Step-by-step getting started guide  
- [Usage Guide](./usage/) - Complete usage instructions
- [Configuration Reference](./configuration.md) - How to configure plowman
- [Changelog](./CHANGELOG.md) - Release history

[build_badge]: https://github.com/spapanik/plowman/actions/workflows/build.yml/badge.svg
[build_url]: https://github.com/spapanik/plowman/actions/workflows/build.yml
[lint_badge]: https://github.com/spapanik/plowman/actions/workflows/lint.yml/badge.svg
[lint_url]: https://github.com/spapanik/plowman/actions/workflows/lint.yml
[tests_badge]: https://github.com/spapanik/plowman/actions/workflows/tests.yml/badge.svg
[tests_url]: https://github.com/spapanik/plowman/actions/workflows/tests.yml
[licence_badge]: https://img.shields.io/pypi/l/plowman
[licence_url]: https://plowman.readthedocs.io/en/stable/LICENSE/
[codecov_badge]: https://codecov.io/github/spapanik/plowman/graph/badge.svg?token=Q20F84BW72
[codecov_url]: https://codecov.io/github/spapanik/plowman
[readthedocs_badge]: https://readthedocs.org/projects/plowman/badge/?version=latest
[readthedocs_url]: https://plowman.readthedocs.io/en/latest/
[pypi_badge]: https://img.shields.io/pypi/v/plowman
[pypi_url]: https://pypi.org/project/plowman
[pepy_badge]: https://pepy.tech/badge/plowman
[pepy_url]: https://pepy.tech/project/plowman
