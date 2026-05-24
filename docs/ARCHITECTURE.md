# Architecture

# High-Level Architecture

```text
                +------------------+
                |  Config Files    |
                +------------------+
                         |
                         v
                +------------------+
                |  MSM Core Engine |
                +------------------+
                   |     |      |
                   |     |      |
          +--------+     |      +---------+
          |              |                |
          v              v                v
 +----------------+ +----------------+ +----------------+
 | Skill Registry | | Profile Engine | | Agent Adapters |
 +----------------+ +----------------+ +----------------+
                                                  |
                                                  v
                                      +----------------------+
                                      | Deployment Layer     |
                                      | (Symlinks / Files)   |
                                      +----------------------+
```

---

# Directory Structure

```text
~/.msm/
│
├── config.yaml
├── registry/
├── registries/
├── profiles/
├── cache/
├── state/
├── logs/
└── templates/
```

---

# Project Local Structure

```text
project-root/
│
├── .msm/
│   ├── project.yaml
│   └── deployed/
│
├── .claude/
├── .codex/
└── .agents/
```

---

# Registry Structure

```text
registry/
│
├── postgres-expert/
│   ├── SKILL.md
│   ├── metadata.yaml
│   ├── prompts/
│   └── templates/
│
└── spark-scala/
```

---

# Internal Components

## Core Engine

Responsible for:
- config parsing
- orchestration
- deployment planning
- validation

---

## Registry Manager

Responsible for:
- adding skills
- removing skills
- cloning and updating Git-backed remote registries
- resolving paths

The writable local registry lives at `~/.msm/registry` by default. Git-backed registries are cloned under `~/.msm/registries/<name>` and are treated as read-only skill sources by MSM. Local skills take precedence over remote skills with the same name.

---

## Profile Engine

Responsible for:
- profile parsing
- skill resolution
- deployment generation

---

## Agent Adapter Layer

Responsible for:
- filesystem paths
- agent-specific conventions
- deployment targets

Each adapter exposes:

```python
class AgentAdapter:
    def global_skill_path(self) -> Path
    def local_skill_path(self, project_root: Path) -> Path
    def validate(self) -> list[str]
```

---

# Deployment Strategy

Preferred deployment method:
- symlink

Fallback:
- file copy

Deployment metadata should be stored in:

```text
~/.msm/state/
```

---

# State Management

MSM should track:
- deployed skills
- deployment targets
- symlink mappings
- profile activations

State should NOT be the source of truth.

Config files remain authoritative.
