from __future__ import annotations

from pathlib import Path

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
    (skill / "SKILL.md").write_text("# PostgreSQL Expert\n", encoding="utf-8")
    (skill / "metadata.yaml").write_text(
        "name: postgres-expert\ndescription: PostgreSQL optimization\n",
        encoding="utf-8",
    )
    return skill
