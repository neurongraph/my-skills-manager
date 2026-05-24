# CLI Specification

# CLI Framework

Use:
- Python
- Typer
- Rich
- uv

---

# Command Structure

```bash
msm [COMMAND] [OPTIONS]
```

---

# Skill Commands

## Add Skill

```bash
msm skill add postgres-expert
```

Options:

```bash
--global
--local
--agent claude-code
```

---

## Remove Skill

```bash
msm skill remove postgres-expert
```

---

## List Skills

```bash
msm skill list
```

---

# Profile Commands

## Apply Profile Globally

```bash
msm profile global-apply aws-data-engineering
```

---

## List Profiles

```bash
msm profile list
```

---

## Validate Profile

```bash
msm profile validate aws-data-engineering
```

---

# Sync Commands

## Sync Environment

```bash
msm sync
```

Purpose:
- reconcile config with deployments
- repair broken symlinks
- update agent directories

---

# Doctor Commands

## Validate Environment

```bash
msm doctor
```

Checks:
- broken symlinks
- missing skills
- invalid configs
- agent path issues

---

# Export Commands

## Export Workstation

```bash
msm export > workstation.yaml
```

---

## Import Workstation

```bash
msm import workstation.yaml
```

---

# Registry Commands

## Add Registry

```bash
msm registry add my-org git@github.com:my-org/skills.git
```

---

## Update Registry

```bash
msm registry update
```

---

# Project Commands

## Initialize Project

```bash
msm init project lakehouse
```

Creates:
- .msm/
- project config
- optional templates

---

# Future Commands

Deferred:

```bash
msm auto-activate
msm mcp sync
msm prompt inspect
```

---

# Suggested Python Stack

## Runtime

- Python 3.12+
- uv
- Typer
- Rich
- PyYAML
- pydantic
- GitPython

---

# Suggested Project Bootstrap

```bash
uv init my_skills_manager
cd my_skills_manager

uv add typer rich pyyaml pydantic gitpython
```

---

# Suggested Package Layout

```text
msm/
│
├── cli/
├── core/
├── registry/
├── profiles/
├── agents/
├── deploy/
├── config/
└── utils/
```
