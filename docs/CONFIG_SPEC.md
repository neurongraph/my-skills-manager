# Configuration Specification

# Global Config

File:

```text
~/.msm/config.yaml
```

Example:

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

profiles:
  default:
    - git-workflow
    - architecture-review
```

---

# Profile Config

Example:

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
      - aws-glue

  codex:
    skills:
      - quick-debugger
```

---

# Project Config

File:

```text
project-root/.msm/project.yaml
```

Example:

```yaml
profile: aws-data-engineering

local_skills:
  - customer-domain-knowledge

agents:

  claude-code:
    additional_skills:
      - architecture-review
```

---

# Skill Metadata

Skill metadata is defined as YAML frontmatter at the top of `SKILL.md`:

```markdown
---
name: postgres-expert
description: PostgreSQL optimization and architecture skill
version: 1.0.0
tags:
  - postgres
  - sql
  - database
---

# PostgreSQL Expert

...
```

Only `description` is required for `msm skill list` to show a description. All other fields are optional.

---

# Export Format

Example:

```yaml
version: 1

machine:
  profiles:
    - aws-data-engineering

  deployed_skills:
    - postgres-expert
    - spark-scala

  agents:
    - claude-code
    - codex
```
