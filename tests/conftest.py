from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from msm.config.io import save_model
from msm.config.models import AgentConfig, GlobalConfig
from msm.config.paths import config_path


@pytest.fixture()
def msm_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "msm-home"
    monkeypatch.setenv("MSM_HOME", str(home))
    return home


@pytest.fixture()
def isolated_agent_config(msm_home: Path) -> GlobalConfig:
    config = GlobalConfig(
        registry_path=msm_home / "registry",
        agents={
            "codex": AgentConfig(
                enabled=True,
                global_path=msm_home / "agents" / "codex" / "global",
                local_path=Path(".codex/skills"),
            ),
            "claude-code": AgentConfig(
                enabled=True,
                global_path=msm_home / "agents" / "claude" / "global",
                local_path=Path(".claude/skills"),
            ),
        },
    )
    save_model(config_path(), config)
    return config


@pytest.fixture()
def sample_skill(tmp_path: Path) -> Path:
    skill = tmp_path / "postgres-expert"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: postgres-expert\ndescription: PostgreSQL optimization\n---\n",
        encoding="utf-8",
    )
    return skill


def run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=MSM Tests",
            "-c",
            "user.email=msm-tests@example.invalid",
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture()
def remote_registry_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "remote-registry"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], check=True, capture_output=True, text=True)
    skill = repo / "spark-scala"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: spark-scala\ndescription: Spark engineering with Scala\n---\n",
        encoding="utf-8",
    )
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-m", "add spark scala")
    return repo
