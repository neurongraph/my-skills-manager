# my_skills_manager

`msm` is a portable AI coding environment manager for skills, profiles, agent-specific deployments, and reproducible workstation configuration.

It manages:

- Local and Git-backed remote skill registries
- Global and project-local skill deployments across multiple AI coding agents
- Reusable profiles that group skills into named bundles
- Workstation export/import for reproducible environment setup
- Environment validation with `doctor`

## Getting Started

```bash
git clone git@github.com:you/my-skills-manager.git ~/Projects/my-skills-manager
cd ~/Projects/my-skills-manager
just setup
```

See the [User Guide](docs/USER_GUIDE.md) for full setup walkthrough, profile creation, project-local deployments, and workstation migration.

## Documentation

- [User Guide](docs/USER_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Product Spec](docs/PRODUCT_SPEC.md)
- [CLI Spec](docs/CLI_SPEC.md)
- [Config Spec](docs/CONFIG_SPEC.md)

## Development

```bash
uv sync
uv run pytest
```

## Status

This is the MVP implementation. Skill inheritance and profile composition are not implemented yet.
