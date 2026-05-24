default:
    @just --list

# Install/reinstall msm as a global CLI tool
install:
    uv tool install --reinstall .

# Install dependencies
sync:
    uv sync

# Run all tests
test:
    uv run pytest

# Run a single test file  e.g: just test-file tests/test_core.py
test-file FILE:
    uv run pytest {{FILE}} -v

# Run a single test by name  e.g: just test-one test_skill_add
test-one NAME:
    uv run pytest -k {{NAME}} -v

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
    msm registry add {{NAME}} {{URL}}
