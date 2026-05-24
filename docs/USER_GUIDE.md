# MSM User Guide

`msm` manages AI coding assistant skills from a local registry and deploys them into agent-specific directories.

It is designed around four ideas:

- The registry is the source of truth for skills.
- Deployments are generated from registry content.
- Deployments use symlinks by default.
- Global and project-local deployments can target multiple coding agents.

## Installation

From this repository:

```bash
uv sync
uv run msm --help
```

For local development, run commands with `uv run msm ...`.

## Default Layout

MSM uses `~/.msm` by default:

```text
~/.msm/
├── config.yaml
├── registry/
├── profiles/
└── state/
```

For testing or isolated use, set `MSM_HOME`:

```bash
MSM_HOME=/tmp/msm-demo uv run msm doctor
```

The first command that loads configuration creates a default `config.yaml` if one does not exist.

## Global Configuration

Default config includes `claude-code` and `codex` agents:

```yaml
version: 1
registry_path: ~/.msm/registry
default_deployment_mode: symlink
agents:
  claude-code:
    enabled: true
    global_path: ~/.claude/skills
    local_path: .claude/skills
  codex:
    enabled: true
    global_path: ~/.config/codex/skills
    local_path: .codex/skills
profiles: {}
registries: {}
```

Edit `~/.msm/config.yaml` to change agent paths or disable an agent.

## Skill Format

A skill is a directory containing at least `SKILL.md`:

```text
postgres-expert/
├── SKILL.md
├── metadata.yaml
├── prompts/
└── templates/
```

`metadata.yaml` is optional. Example:

```yaml
name: postgres-expert
description: PostgreSQL optimization and architecture skill
version: 1.0.0
tags:
  - postgres
  - sql
files:
  - SKILL.md
```

## Add and Deploy a Skill

Install a local skill directory into the registry and deploy it globally:

```bash
uv run msm skill add postgres-expert --from ./postgres-expert
```

Deploy only to one agent:

```bash
uv run msm skill add postgres-expert --agent codex
```

Deploy to project-local agent paths instead of global paths:

```bash
uv run msm skill add postgres-expert --local --agent codex
```

Deploy to both global and project-local paths:

```bash
uv run msm skill add postgres-expert --global --local
```

If neither `--global` nor `--local` is provided, MSM deploys globally.

## List and Remove Skills

List skills in the registry:

```bash
uv run msm skill list
```

Remove a skill from generated deployments and from the registry:

```bash
uv run msm skill remove postgres-expert
```

## Profiles

Profiles live in `~/.msm/profiles/<name>.yaml`.

Example `~/.msm/profiles/aws-data-engineering.yaml`:

```yaml
name: aws-data-engineering
description: AWS lakehouse engineering environment
global_skills:
  - git-workflow
  - architecture-review
agents:
  claude-code:
    skills:
      - spark-scala
      - postgres-expert
  codex:
    skills:
      - quick-debugger
```

List profiles:

```bash
uv run msm profile list
```

Validate that referenced skills and agents exist:

```bash
uv run msm profile validate aws-data-engineering
```

Apply a profile:

```bash
uv run msm profile apply aws-data-engineering
```

Profile `global_skills` are deployed to all enabled agents. Agent-specific skills are deployed only to that agent.

## Project-Local Configuration

Initialize a project:

```bash
uv run msm init project --profile aws-data-engineering
```

This creates:

```text
.msm/
├── project.yaml
└── deployed/
```

Example `.msm/project.yaml`:

```yaml
profile: aws-data-engineering
local_skills:
  - customer-domain-knowledge
agents:
  claude-code:
    additional_skills:
      - architecture-review
```

Apply project config:

```bash
uv run msm sync
```

`sync` applies the configured profile, deploys `local_skills` to each enabled agent's local path, and deploys agent-specific `additional_skills`.

## Doctor

Run environment checks:

```bash
uv run msm doctor
```

Doctor reports:

- Invalid global configuration
- Missing agent path settings
- Missing deployed skill sources
- Broken deployment symlinks

A healthy environment prints:

```text
No issues found
```

## Export and Import

Export current deployment state:

```bash
uv run msm export > workstation.yaml
```

Example export:

```yaml
version: 1
machine:
  profiles:
    - aws-data-engineering
  deployed_skills:
    - postgres-expert
  agents:
    - codex
```

Import a workstation file:

```bash
uv run msm import workstation.yaml
```

Import redeploys the listed skills from the local registry. The skills must already exist in the registry.

## Registry References

Record an external registry reference:

```bash
uv run msm registry add my-org git@github.com:my-org/skills.git
```

List configured external registry references:

```bash
uv run msm registry update
```

The MVP stores external registry metadata only. Remote clone/update behavior is deferred.

## Common Workflows

Create and deploy one skill:

```bash
mkdir -p postgres-expert
printf '# PostgreSQL Expert\n' > postgres-expert/SKILL.md
uv run msm skill add postgres-expert --from ./postgres-expert --agent codex
uv run msm doctor
```

Use an isolated demo home:

```bash
export MSM_HOME=/tmp/msm-demo
uv run msm doctor
uv run msm skill list
```

Prepare a project:

```bash
uv run msm init project --profile aws-data-engineering
uv run msm sync
```

## Current Limitations

- Remote registry clone/update is not implemented.
- Profile composition is not implemented.
- Skill inheritance is not implemented.
- Marketplace hosting and GUI features are out of scope for the MVP.
