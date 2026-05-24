# my_skills_manager

`msm` is a portable AI coding environment manager for skills, profiles, agent-specific deployments, and reproducible workstation configuration.

It manages:

- Local skill registries
- Global and project-local skill deployments
- Agent-specific skill paths
- Reusable profiles
- Workstation export/import files
- Environment validation with `doctor`

## Quick Start

```bash
uv sync
uv run msm --help
uv run msm doctor
```

Create a simple skill and deploy it to Codex:

```bash
mkdir -p postgres-expert
printf '# PostgreSQL Expert\n' > postgres-expert/SKILL.md
uv run msm skill add postgres-expert --from ./postgres-expert --agent codex
```

List registry skills:

```bash
uv run msm skill list
```

Initialize a project-local MSM config:

```bash
uv run msm init project
uv run msm sync
```

## Documentation

- [User Guide](docs/USER_GUIDE.md)
- [Product Spec](docs/PRODUCT_SPEC.md)
- [CLI Spec](docs/CLI_SPEC.md)
- [Config Spec](docs/CONFIG_SPEC.md)
- [Architecture](docs/ARCHITECTURE.md)

## CLI Overview

```bash
msm skill add postgres-expert --from ./postgres-expert --agent codex
msm skill remove postgres-expert
msm skill list
msm profile apply aws-data-engineering
msm profile validate aws-data-engineering
msm sync
msm doctor
msm export > workstation.yaml
msm import workstation.yaml
msm registry add my-org git@github.com:my-org/skills.git
msm init project --profile aws-data-engineering
```

## Development

```bash
uv run msm --help
uv run pytest
```

## Status

This is the MVP implementation. Remote registry clone/update behavior, skill inheritance, profile composition, and GUI features are not implemented yet.
