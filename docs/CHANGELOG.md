# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to [Semantic Versioning].

## [Unreleased]

### Added

- Added a harvest command

## [0.3.1] - 2026-06-24

### Fixed

- Don't break on missing files during deployment (#274a887)
- Remove unused import for cleaner codebase (#750d7e7)

## [0.3.0] - 2026-06-24

### Added

- Show unified diffs between source and destination files with colored output (#d29247d)
- Improve user-facing messages for better clarity (#9a7c75b)

### Changed

- Enhanced verbosity levels to show diffs at level 2+

## [0.2.1] - 2026-06-24

### Fixed

- Add missing dependency to ensure proper functionality (#3a8e3bb)

## [0.2.0] - 2026-06-24

### Added

- Optionally allow symlinks to act as files instead of being overwritten (#4355fe5)
- Support Jinja2 template rendering with variables (#5dd6d4a)
- Dry-run mode to preview changes without making modifications (#0a6fa43)

### Changed

- Separate hash checking and file copying into distinct methods for better code organization (#5081d9d)
- Modernize configuration system with improved structure (#ab86130)

### Internal

- Add comprehensive test suite (#02eeb62)

## [0.1.0] - 2026-06-24

### Added

- Initial release of plowman
- Basic `sow` command for deploying dotfiles from granaries
- Configuration system using YAML files
- Estate file tracking for automatic cleanup of orphaned files
- SHA256 hashing to skip unchanged files
- Recursive file scanning in granary directories
- Automatic directory creation for destination paths
- Command-line interface with verbosity flags

---

[Keep a Changelog]: https://keepachangelog.com/en/1.1.0/
[Semantic Versioning]: https://semver.org/spec/v2.0.0.html
[Unreleased]: https://github.com/spapanik/plowman/compare/v0.3.1...main
[0.3.1]: https://github.com/spapanik/plowman/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/spapanik/plowman/compare/v0.2.1...v0.3.0
[0.2.1]: https://github.com/spapanik/plowman/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/spapanik/plowman/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/spapanik/plowman/releases/tag/v0.1.0
