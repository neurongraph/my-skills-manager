# MSM MVP Design

## Goal

Build the first working version of `my_skills_manager` as a Python CLI named `msm`, matching the specifications in `docs/PRODUCT_SPEC.md`, `docs/CLI_SPEC.md`, `docs/CONFIG_SPEC.md`, and `docs/ARCHITECTURE.md`.

## Architecture

MSM will be a small Typer application layered around a reusable core package:

- `msm.config`: pydantic models and YAML load/save helpers for global config, profiles, project config, metadata, export files, and state.
- `msm.registry`: local filesystem registry operations for installing, removing, listing, and resolving skills.
- `msm.agents`: agent adapters for configured filesystem targets, including built-in defaults for `claude-code` and `codex`.
- `msm.deploy`: symlink-first materialization of registry skills into global or project-local agent skill directories, with copy fallback.
- `msm.core`: orchestration for CLI commands.
- `msm.cli`: Typer command tree.

Config files remain authoritative. State files only describe what MSM deployed, where it deployed it, and whether a target used symlinks or copies.

## Behavior

The MVP supports:

- `msm skill add|remove|list`
- `msm profile apply|list|validate`
- `msm sync`
- `msm doctor`
- `msm export`
- `msm import`
- `msm registry add|update`
- `msm init project`

The implementation uses `~/.msm` by default but allows tests and callers to override the home path through `MSM_HOME`. Project-local commands use the current working directory unless a project root is explicitly passed through the core APIs.

## Error Handling

Commands raise clear Typer errors for invalid skill names, missing profiles, missing config, missing registry paths, and broken deployments. `doctor` reports issues without mutating files. `sync` repairs generated deployment targets according to config and project files.

## Testing

Tests will cover config parsing, registry operations, profile skill resolution, symlink/copy deployment, doctor checks, export/import, project initialization, and CLI command behavior using isolated temporary directories.

## Notes

This workspace was not initialized as a Git repository when implementation began, so the normal design-spec commit step could not be performed.
