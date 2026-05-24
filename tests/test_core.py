from __future__ import annotations

import yaml
from pathlib import Path

from msm.config.io import save_model
from msm.config.models import ExportConfig, ExportMachine, ProfileConfig, ProjectConfig
from msm.config.paths import config_path, profiles_path
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


def test_skill_list_includes_metadata_description(isolated_agent_config, sample_skill):
    service = MSMService()
    service.registry.install_from_path(sample_skill)

    skills = service.skill_list()

    assert skills[0].name == "postgres-expert"
    assert skills[0].metadata is not None
    assert skills[0].metadata.description == "PostgreSQL optimization"


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


def test_project_sync_deploys_profile_skills_locally(
    isolated_agent_config, sample_skill, tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    service = MSMService()
    service.registry.install_from_path(sample_skill)
    save_model(
        profiles_path() / "data.yaml",
        ProfileConfig(name="data", global_skills=["postgres-expert"]),
    )
    save_model(tmp_path / ".msm" / "project.yaml", ProjectConfig(profile="data"))

    messages = service.sync()

    assert messages == [
        f"Deployed: {tmp_path / '.codex' / 'skills' / 'postgres-expert'}",
        f"Deployed: {tmp_path / '.claude' / 'skills' / 'postgres-expert'}",
    ]
    assert (tmp_path / ".codex" / "skills" / "postgres-expert").is_symlink()
    assert not (isolated_agent_config.agents["codex"].global_path / "postgres-expert").exists()
    assert not (isolated_agent_config.agents["claude-code"].global_path / "postgres-expert").exists()


def test_doctor_reports_duplicate_remote_and_local_skill(
    isolated_agent_config, sample_skill, remote_registry_repo
):
    service = MSMService()
    service.registry.install_from_path(sample_skill, "spark-scala")
    config = service.registry.save_registry_reference("team", str(remote_registry_repo))
    save_model(config_path(), config)

    issues = MSMService().doctor()

    assert "Duplicate skill 'spark-scala' found in: local, team" in issues


def test_profile_apply_local_deploys_and_writes_project_yaml(
    isolated_agent_config, sample_skill, tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    service = MSMService()
    service.registry.install_from_path(sample_skill)
    save_model(
        profiles_path() / "data.yaml",
        ProfileConfig(name="data", global_skills=["postgres-expert"]),
    )

    service.profile_apply_local("data")

    project_yaml = tmp_path / ".msm" / "project.yaml"
    assert project_yaml.exists()
    project = ProjectConfig.model_validate(
        yaml.safe_load(project_yaml.read_text())
    )
    assert project.profile == "data"
    assert (tmp_path / ".codex" / "skills" / "postgres-expert").is_symlink()


def test_export_embeds_full_profile_and_registries(
    isolated_agent_config, sample_skill, tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    service = MSMService()
    service.registry.install_from_path(sample_skill)
    save_model(
        profiles_path() / "data.yaml",
        ProfileConfig(name="data", global_skills=["postgres-expert"]),
    )
    service.skill_add("postgres-expert", agent="codex")
    service.config = service.config.model_copy(
        update={"registries": {"team": "git@github.com:org/skills.git"}}
    )

    export = service.export()

    assert "data" in export.machine.profiles
    assert export.machine.profiles["data"].global_skills == ["postgres-expert"]
    assert export.machine.registries == {"team": "git@github.com:org/skills.git"}


def test_import_writes_profiles_and_deploys_skills(
    isolated_agent_config, sample_skill, tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    service = MSMService()
    service.registry.install_from_path(sample_skill)

    workstation = tmp_path / "workstation.yaml"
    save_model(
        workstation,
        ExportConfig(
            machine=ExportMachine(
                profiles={"data": ProfileConfig(name="data", global_skills=["postgres-expert"])},
                deployed_skills=["postgres-expert"],
                agents=["codex"],
            )
        ),
    )

    messages = service.import_file(workstation)

    assert (profiles_path() / "data.yaml").exists()
    assert any("Imported profile: data" in m for m in messages)
    assert any("Deployed:" in m for m in messages)
