# my_skills_manager (MSM)

## Vision

my_skills_manager (MSM) is a portable AI coding environment manager.

It manages:
- SKILL.md files
- agent-specific skill deployments
- global vs local skill scopes
- reusable skill profiles
- AI coding agent configurations
- project archetypes
- reproducible workstation environments

The goal is to make AI-assisted coding environments:
- portable
- composable
- reproducible
- version controlled
- multi-agent aware

MSM is NOT just a wrapper around `npx skills`.

It is intended to become:
- a declarative orchestration layer
- for AI coding environments

---

# Core Concepts

## Skill

A reusable capability package.

Example:
- postgres-expert
- spark-scala
- aws-data-platform
- architecture-review

A skill may contain:
- SKILL.md
- prompts
- templates
- helper files
- metadata

---

## Profile

A reusable collection of skills and deployment rules.

Profiles describe:
- which skills to activate
- which agents receive them
- global vs project-local deployment
- optional project templates

Example:
- aws-data-engineering
- ai-prototyping
- photography-workflow

---

## Agent

An AI coding assistant platform.

Examples:
- Claude Code
- Codex
- OpenCode
- Cursor
- Gemini CLI

MSM should abstract agent-specific filesystem behavior.

---

## Deployment

The materialization of skills into:
- global directories
- project directories
- agent-specific paths

Deployments should preferably use symlinks.

---

## Registry

Canonical storage location for skills.

The registry is the source of truth.

Deployments are generated from the registry.

---

# Goals

## Primary Goals

- Manage global vs project-local skills
- Support multiple coding agents
- Allow portable workstation replication
- Enable declarative configuration
- Support reusable skill profiles
- Support symlink-based deployment
- Maintain compatibility with `npx skills`

---

## Secondary Goals

- Project archetypes
- MCP configuration deployment
- Prompt orchestration
- Auto-activation
- Semantic skill discovery

---

# Non-Goals (Initial Version)

- Skill inheritance
- Cloud synchronization
- Marketplace hosting
- GUI application
- Agent execution orchestration
- Runtime prompt injection

---

# Design Principles

## Declarative First

Configuration should be:
- git friendly
- readable
- deterministic

YAML preferred.

---

## Registry is Immutable

Registry content should be treated as canonical.

Deployments are generated artifacts.

---

## Symlink-Based Deployments

Avoid copying files whenever possible.

Advantages:
- deduplication
- easier updates
- version consistency

---

## Agent-Agnostic Core

MSM must not hardcode logic for one agent.

All agent behavior should be adapter-based.

---

## Portable Workstations

A developer should be able to:

```bash
git clone my-dev-env
msm sync
```

and recreate the same environment on another machine.

---

# MVP Scope

## Included

- Skill registry
- Skill install/remove
- Global deployments
- Project-local deployments
- Multi-agent support
- Profiles
- Config export/import
- Symlink deployments
- Validation/doctor command
- Git-backed remote registry clone/update

---

## Deferred

- Skill inheritance
- Auto-discovery
- AI-generated profiles
- Profile composition
