# MSM User Guide

`msm` manages AI coding assistant skills and deploys them into agent-specific directories for Claude Code, Codex, and other agents.

Skills come from Git-backed registries. Profiles group skills into reusable bundles — some deployed globally across all projects, others locally per-project. A single export/import command moves the full setup to a new machine.

---

## Workflow 1: Set Up a New Workstation

Use this when you are setting up MSM for the first time — connecting skill registries, reviewing available skills, and creating profiles for your common work contexts.

### 1. Install MSM

```bash
git clone git@github.com:you/my-skills-manager.git ~/Projects/my-skills-manager
cd ~/Projects/my-skills-manager
just setup
```

`just setup` installs dependencies, installs `msm` as a global CLI tool, and runs `msm doctor` to bootstrap `~/.msm/config.yaml`. A healthy workstation prints `No issues found`.

Default agents configured out of the box:

| Agent | Global path | Local path |
|---|---|---|
| `claude-code` | `~/.claude/skills` | `.claude/skills` |
| `codex` | `~/.codex/skills` | `.codex/skills` |
| `antigravity` | `~/.gemini/antigravity/skills` | `.agents/skills` |
| `opencode` | `~/.agents/skills` | `.agents/skills` |
| `bob` | `~/.bob/skills` | `.bob/skills` |
| `pi` | `~/.agents/skills` | `.agents/skills` |

To disable an agent or change its paths, edit `~/.msm/config.yaml`.

### 2. Connect Skill Registries

Skills live in Git repositories. To add a curated set of example registries in one shot:

```bash
just add-example-skill-registries
```

Or register any Git-backed registry manually:

```bash
msm registry add personal git@github.com:you/skills.git
```

Each registry is cloned into `~/.msm/registries/<name>`. Pull the latest from all registered repos at any time:

```bash
msm registry update
```

To see everything available across all registries:

```bash
msm skill list
```

The `Source` column shows which registry each skill came from. If the same skill name exists in both a remote registry and your local registry (`~/.msm/registry`), the local one wins.

### 3. Add a One-Off Skill Locally

For a skill that isn't in any registry yet, import it directly:

```bash
msm skill add my-skill --from ~/Downloads/my-skill
```

This copies the skill into `~/.msm/registry`. Prefer committing skills to a Git registry for reproducibility — one-off local skills won't appear in an export's registry list.

A skill directory needs at minimum a `SKILL.md` (the prompt content). An optional `metadata.yaml` adds description and tags:

```yaml
name: postgres-expert
description: PostgreSQL optimization and query tuning
version: 1.0.0
tags:
  - postgres
  - sql
```

### 4. Create Profiles

A profile groups skills into a reusable bundle. Scaffold one with all configured agents pre-populated:

```bash
msm profile new office-work --description "Office productivity — presentations, meeting prep, notes"
```

This creates `~/.msm/profiles/office-work.yaml` with every enabled agent listed and placeholder skill names to replace. Open it in your editor and update the skills:

```bash
$EDITOR ~/.msm/profiles/office-work.yaml
```

```yaml
name: office-work
description: Office productivity — presentations, meeting prep, notes
global_skills:
  - pptx
agents:
  claude-code:
    skills:
      - client-meeting-prep
      - obsidian-tasks
  codex:
    skills:
      - client-meeting-prep
      - obsidian-tasks
```

**`global_skills`** are deployed to all enabled agents at the workstation level — available in every project.

**`agents.<name>.skills`** are intended for project-local deployment. They go to `.claude/skills`, `.codex/skills`, etc. inside the project folder when you run `local-apply` or `sync`.

Remove any agent blocks you don't need for this profile, then validate:

```bash
msm profile validate office-work
```

### 5. Deploy Global Skills

Push a profile's global skills to the workstation so they're available in every project:

```bash
msm profile global-apply office-work
```

Run `msm doctor` at any time to verify the environment is consistent.

---

## Workflow 2: Start a New Project

Use this when you open a new project folder and want to load the right skills into it for your AI coding agents.

### 1. Pick or Create a Profile

Review what profiles exist:

```bash
msm profile list
msm profile validate office-work
```

If an existing profile fits, use it. If you need something different, either:

**Add a skill to an existing profile** — edit the YAML directly:

```bash
$EDITOR ~/.msm/profiles/office-work.yaml
```

Add to `global_skills` for workstation-wide availability, or to `agents.<name>.skills` for project-local use.

**Create a new profile** — scaffold it with all configured agents pre-populated:

```bash
msm profile new aws-data-engineering --description "AWS lakehouse engineering"
$EDITOR ~/.msm/profiles/aws-data-engineering.yaml
```

Replace the placeholder skills with the ones you want, remove agents you don't need, then validate:

```bash
msm profile validate aws-data-engineering
```

If the profile references a skill that doesn't exist yet, add it to a registry first (`msm skill add --from ...` or commit it to your Git registry and run `msm registry update`).

### 2. Apply the Profile to the Project

```bash
cd ~/Projects/my-project
msm profile local-apply aws-data-engineering
```

This deploys the profile's agent skills into the project's local agent directories:

```text
~/Projects/my-project/
├── .claude/skills/spark-scala   → ~/.msm/registries/...
├── .claude/skills/postgres-expert
└── .codex/skills/spark-scala
```

It also writes `.msm/project.yaml` so the profile is remembered:

```yaml
profile: aws-data-engineering
```

From this point on, running `msm sync` in the project folder re-applies the profile — useful after `msm registry update` picks up new skill versions, or after editing the profile to add or remove skills.

### 3. Re-sync After Profile or Registry Changes

When you edit a profile or pull new skill versions:

```bash
msm registry update   # optional: pull latest skill versions
cd ~/Projects/my-project && msm sync
```

`sync` reconciles the project against `.msm/project.yaml` — deploying skills added to the profile and removing skills that were dropped from it.

---

## Workflow 3: Move to a New Workstation

Use this to replicate your full MSM environment on a new machine — registries, profiles, and deployed skills.

### 1. Export on the Source Machine

```bash
msm export > workstation.yaml
```

The export bundles everything needed:

```yaml
version: 1
machine:
  profiles:
    office-work:
      name: office-work
      description: Office productivity — presentations, meeting prep, notes
      global_skills:
        - pptx
      agents:
        claude-code:
          skills:
            - client-meeting-prep
            - obsidian-tasks
        codex:
          skills:
            - client-meeting-prep
            - obsidian-tasks
  deployed_skills:
    - client-meeting-prep
    - obsidian-tasks
    - pptx
  agents:
    - claude-code
    - codex
  registries:
    personal: git@github.com:you/skills.git
    team: git@github.com:my-org/shared-skills.git
```

Commit `workstation.yaml` to a dotfiles repo or copy it to the new machine.

### 2. Import on the New Machine

Install MSM, then:

```bash
msm import workstation.yaml
```

Import runs in order:

1. **Writes all profiles** to `~/.msm/profiles/` from the embedded profile configs.
2. **Registers** any remote registries not yet configured and clones them.
3. **Runs `registry update`** to ensure all clones are current.
4. **Redeploys all listed skills** from the now-available registries.

### 3. Re-apply Global Skills

`import` restores skills and profiles but does not re-run `global-apply`. Do that once after import:

```bash
msm profile global-apply office-work
```

### 4. Restore Project-Local Skills

For each project, re-run sync:

```bash
cd ~/Projects/my-project && msm sync
```

`sync` reads the project's `.msm/project.yaml` (which you committed to the project repo) and re-deploys the correct profile locally.

---

## Reference

### Commands

| Command | What it does |
|---|---|
| `msm doctor` | Validate environment, report issues |
| `msm skill list` | List all skills across registries |
| `msm skill add <name> --from <dir>` | Import a local directory into the registry |
| `msm skill remove <name>` | Remove skill from registry and all deployments |
| `msm registry add <name> <url>` | Register and clone a Git registry |
| `msm registry update` | Pull latest from all registered Git registries |
| `msm profile new <name>` | Scaffold a new profile with all agents pre-populated |
| `msm profile list` | List all profiles |
| `msm profile validate <name>` | Check all skills and agents in a profile exist |
| `msm profile global-apply <name>` | Deploy profile skills to global agent paths |
| `msm profile local-apply <name>` | Deploy profile skills to project-local paths, write `.msm/project.yaml` |
| `msm sync` | Reconcile project against its profile — deploy added skills, remove dropped ones |
| `msm export > file.yaml` | Export full workstation state |
| `msm import <file>` | Restore workstation from export |

### Skill Deployment Scopes

**Global** (`msm profile global-apply`): Skills deployed to `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills`, etc. Available in every project on the machine.

**Local** (`msm profile local-apply`, `msm sync`): Skills deployed to `.claude/skills`, `.codex/skills` inside the current project folder. Only visible to that project's agent session.

### Current Limitations

- Profile composition (inheriting from another profile) is not implemented.
- Skill inheritance is not implemented.
