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
├── registries/
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

List skills and descriptions in the registry:

```bash
uv run msm skill list
```

Remove a skill from generated deployments and from the registry:

```bash
uv run msm skill remove postgres-expert
```

## Workflow: Maintain a Skills Registry and Profiles

Use this workflow when you are curating reusable skills and profile definitions for a workstation or team.

### Choose the Registry Location

The default registry is:

```text
~/.msm/registry
```

The recommended registry source of truth is a Git repository. MSM clones registered Git repositories into `~/.msm/registries/<name>` and reads skills from those clones.

Recommended structure:

```text
skills-registry/
├── postgres-expert/
│   ├── SKILL.md
│   └── metadata.yaml
└── architecture-review/
    ├── SKILL.md
    └── metadata.yaml
```

### Add Skills from Elsewhere

The preferred workflow is to add or edit skills in a Git-backed skills registry, commit, push, and then update MSM:

```bash
cd ~/Projects/skills-registry
mkdir -p postgres-expert
printf '# PostgreSQL Expert\n' > postgres-expert/SKILL.md
$EDITOR postgres-expert/metadata.yaml
git add postgres-expert
git commit -m "add postgres expert skill"
git push

cd ~/Projects/my-skills-manager
uv run msm registry update
uv run msm skill list
```

You can still import a local skill directory into the writable local registry:

```bash
uv run msm skill add postgres-expert --from ~/Downloads/postgres-expert --agent codex
```

Treat `skill add --from` as a convenience path for scratch or imported skills. For reproducible use, commit skills to a Git-backed registry first.

The `--from` directory must contain `SKILL.md`. If the skill includes `metadata.yaml`, `msm skill list` shows its description.

Register an external registry reference:

```bash
uv run msm registry add team-skills git@github.com:my-org/skills.git
```

`registry add` stores the registry reference in config and clones it into:

```text
~/.msm/registries/team-skills
```

Update all registered Git registries:

```bash
uv run msm registry update
```

`registry update` runs `git pull --ff-only` for existing clones. If a configured clone is missing, it clones it again.

### Review Registered Skills

List registered skills with descriptions and sources:

```bash
uv run msm skill list
```

Descriptions come from each skill's `metadata.yaml`:

```yaml
name: postgres-expert
description: PostgreSQL optimization and architecture skill
```

The `Source` column is `local` for the writable local registry, or the registered Git registry name for remote skills. If a skill exists in both local and remote registries, the local registry wins. `msm doctor` reports duplicate skill names.

### Create and Maintain Profiles

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

Deploy a profile globally to the workstation:

```bash
uv run msm profile global-apply aws-data-engineering
```

`global-apply` deploys profile skills to each agent's configured global path. Use it for baseline workstation skills that should be available across all projects.

To add a new global skill to a profile, edit `global_skills`:

```yaml
global_skills:
  - git-workflow
  - architecture-review
  - security-review
```

To add a new agent-specific skill, edit the relevant agent entry:

```yaml
agents:
  codex:
    skills:
      - quick-debugger
      - python-refactor
```

To add a new agent to a profile, add a new key under `agents`. The agent must also exist in `~/.msm/config.yaml`:

```yaml
agents:
  opencode:
    skills:
      - terminal-workflow
```

## Workflow: Initialize a Project from a Profile

Initialize a project:

```bash
cd ~/Projects/customer-lakehouse
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

`sync` deploys the configured profile into project-local agent paths. It does not deploy the profile to global workstation paths.

For the example above, profile skills are deployed into paths such as:

```text
~/Projects/customer-lakehouse/.codex/skills/
~/Projects/customer-lakehouse/.claude/skills/
```

`sync` also deploys `local_skills` to each enabled agent's local path, and deploys agent-specific `additional_skills`.

Use `msm profile global-apply <profile>` only when you explicitly want the profile deployed globally to the workstation.

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

Add and clone a Git-backed registry:

```bash
uv run msm registry add my-org git@github.com:my-org/skills.git
```

Update configured Git-backed registries:

```bash
uv run msm registry update
```

Remote registries are read-only from MSM's point of view. Add or edit skills in the source Git repository, push the changes, then run `msm registry update`.

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

- Profile composition is not implemented.
- Skill inheritance is not implemented.
- Marketplace hosting and GUI features are out of scope for the MVP.
