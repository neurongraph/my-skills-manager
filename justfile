default:
    @just --list

# Install/reinstall msm as a global CLI tool
install:
    uv tool install --reinstall .

# Bootstrap a fresh msm environment: install deps, install tool, create ~/.msm/config.yaml
setup:
    uv sync
    uv tool install --reinstall .
    msm doctor

add-example-skill-registries:
    msm registry add anthropics https://github.com/anthropics/skills
    msm registry add superpowers https://github.com/obra/superpowers
    msm registry add surjit_skills https://github.com/neurongraph/skills_repo
    msm registry add obsidian https://github.com/kepano/obsidian-skills

# Install dependencies
sync:
    uv sync

# Run all tests
test:
    uv run pytest

# Run a single test file  e.g: just test-file tests/test_core.py
test-file FILE:
    uv run pytest {{ FILE }} -v

# Run a single test by name  e.g: just test-one test_skill_add
test-one NAME:
    uv run pytest -k {{ NAME }} -v

# Check environment health
doctor:
    msm doctor

# Show current workstation export
export:
    msm export

# List all skills across registries
skills:
    msm skill list

# List all profiles
profiles:
    msm profile list

# Pull latest from all registered Git registries
update:
    msm registry update

# Add a Git-backed skill registry  e.g: just add-registry personal git@github.com:you/skills.git
add-registry NAME URL:
    msm registry add {{ NAME }} {{ URL }}
