# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Run the CLI
uv run msm --help

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_core.py

# Run a specific test
uv run pytest tests/test_core.py::test_skill_add_and_export

# Check environment health
uv run msm doctor
```

## Architecture

`msm` is a Python CLI (Typer + Pydantic) that manages AI coding skill deployments across agents (Claude Code, Codex).

**Request flow:**

```
CLI (msm/cli/app.py)
  → MSMService (msm/core/service.py)   ← central orchestrator
      ├── RegistryManager              ← resolves skill paths
      ├── AgentAdapter layer           ← maps agents to filesystem paths
      └── DeploymentManager            ← materializes skills (symlinks or copy)
```

**Key modules:**
- `msm/cli/app.py` — Typer subcommands: `skill`, `profile`, `registry`, `init`, `sync`, `doctor`, `export`/`import`
- `msm/core/service.py` — `MSMService`: all business logic lives here
- `msm/config/models.py` — Pydantic models: `GlobalConfig`, `ProfileConfig`, `ProjectConfig`, `SkillMetadata`
- `msm/config/io.py` — YAML load/save helpers; `load_global_config()` auto-creates `~/.msm/config.yaml`
- `msm/config/state.py` — Deployment state tracking (`~/.msm/state/deployments.yaml`); not authoritative, used for doctor/validation
- `msm/registry/manager.py` — `RegistryManager`: install from path, resolve skill, list; local registry takes precedence over remotes
- `msm/agents/adapters.py` — `AgentAdapter`, `enabled_adapters()`, `selected_adapters()`; agents have global (`~/.claude/`) and local (`.claude/`) skill paths
- `msm/agents/defaults.py` — Default agent configs for `claude-code` and `codex`
- `msm/deploy/manager.py` — `DeploymentManager.deploy_skill()`: symlinks preferred, falls back to `copytree`

**Filesystem layout at runtime:**

```
~/.msm/
├── config.yaml          # GlobalConfig (agents, registries, default_deployment_mode)
├── registry/            # Local skill registry (source of truth for local skills)
├── registries/<name>/   # Cloned remote Git registries (read-only)
├── profiles/            # ProfileConfig YAML files
└── state/deployments.yaml

project-root/
├── .msm/project.yaml    # ProjectConfig (profile, local_skills, agent overrides)
└── .claude/skills/      # Project-local deployed skills (claude-code)
```

**Skill structure** (a directory with at minimum `SKILL.md`):
```
postgres-expert/
├── SKILL.md          # required
├── metadata.yaml     # optional: name, description, version, tags
└── prompts/          # optional supporting files
```

## Design Patterns

- **Registry precedence**: Local (`~/.msm/registry`) overrides remote registries with same skill name.
- **Scope**: `global_scope=True` deploys to `~/.claude/skills`; `local_scope=True` deploys to `.claude/skills` relative to project root.
- **State is not authoritative**: Config files declare intent; `~/.msm/state/deployments.yaml` records what was deployed. `msm doctor` validates consistency between them.
- **MSM_HOME**: Set this env var to override the default `~/.msm` base directory (used in tests for isolation).

## Testing

Fixtures are in `tests/conftest.py`:
- `msm_home` — isolated temp dir via `MSM_HOME` env var
- `isolated_agent_config` — `GlobalConfig` with codex and claude-code pre-configured
- `sample_skill` — a `postgres-expert` skill directory with `SKILL.md` and `metadata.yaml`
- `remote_registry_repo` — bare Git repo mimicking a remote skill registry

## Documentation

Detailed specs in `docs/`:
- `ARCHITECTURE.md`, `PRODUCT_SPEC.md`, `CLI_SPEC.md`, `CONFIG_SPEC.md`, `USER_GUIDE.md`
