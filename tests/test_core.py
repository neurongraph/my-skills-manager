from __future__ import annotations

from pathlib import Path

from msm.config.io import save_model
from msm.config.models import ProfileConfig
from msm.config.paths import profiles_path
from msm.core.service import MSMService


def test_skill_add_and_export(isolated_agent_config, sample_skill, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    service = MSMService()
    service.registry.install_from_path(sample_skill)

    messages = service.skill_add("postgres-expert", agent="codex")
    export = service.export()

    assert messages[0].startswith("Deployed:")
    assert export.machine.deployed_skills == ["postgres-expert"]
    assert export.machine.agents == ["codex"]


def test_profile_validate_reports_missing_skill(msm_home):
    save_model(
        profiles_path() / "aws-data-engineering.yaml",
        ProfileConfig(name="aws-data-engineering", global_skills=["missing-skill"]),
    )

    issues = MSMService().profile_validate("aws-data-engineering")

    assert issues == ["Missing skill: missing-skill"]


def test_init_project_creates_project_config(msm_home, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    path = MSMService().init_project("lakehouse")

    assert path == tmp_path / ".msm" / "project.yaml"
    assert path.exists()
    assert (tmp_path / ".msm" / "deployed").exists()
