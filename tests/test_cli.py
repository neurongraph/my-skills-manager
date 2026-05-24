from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from msm.cli.app import app


runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Portable AI coding environment manager" in result.output


def test_cli_skill_add_from_path(msm_home, isolated_agent_config, sample_skill):
    result = runner.invoke(
        app,
        ["skill", "add", "postgres-expert", "--from", str(sample_skill), "--agent", "codex"],
        env={"MSM_HOME": str(msm_home)},
    )

    assert result.exit_code == 0
    assert "Deployed:" in result.output


def test_cli_skill_list_shows_descriptions(msm_home, isolated_agent_config, sample_skill):
    runner.invoke(
        app,
        ["skill", "add", "postgres-expert", "--from", str(sample_skill), "--agent", "codex"],
        env={"MSM_HOME": str(msm_home)},
    )

    result = runner.invoke(app, ["skill", "list"], env={"MSM_HOME": str(msm_home)})

    assert result.exit_code == 0
    assert "postgres-expert" in result.output
    assert "PostgreSQL optimization" in result.output
    assert "local" in result.output


def test_cli_registry_add_clones_remote(msm_home, isolated_agent_config, remote_registry_repo):
    result = runner.invoke(
        app,
        ["registry", "add", "team", str(remote_registry_repo)],
        env={"MSM_HOME": str(msm_home)},
    )

    assert result.exit_code == 0
    assert "Registered and cloned team" in result.output

    list_result = runner.invoke(app, ["skill", "list"], env={"MSM_HOME": str(msm_home)})

    assert list_result.exit_code == 0
    assert "spark-scala" in list_result.output
    assert "Spark engineering with Scala" in list_result.output
    assert "team" in list_result.output


def test_cli_profile_apply_command_is_removed():
    result = runner.invoke(app, ["profile", "apply", "example"])

    assert result.exit_code != 0
    assert "No such command" in result.output


def test_cli_doctor_clean(msm_home):
    result = runner.invoke(app, ["doctor"], env={"MSM_HOME": str(msm_home)})

    assert result.exit_code == 0
    assert "No issues found" in result.output


def test_cli_profile_local_apply_deploys_skills(
    msm_home, isolated_agent_config, sample_skill
):
    from msm.config.io import save_model
    from msm.config.models import ProfileConfig
    from msm.config.paths import profiles_path

    runner.invoke(
        app,
        ["skill", "add", "postgres-expert", "--from", str(sample_skill), "--agent", "codex"],
        env={"MSM_HOME": str(msm_home)},
    )
    save_model(
        profiles_path() / "data.yaml",
        ProfileConfig(name="data", global_skills=["postgres-expert"]),
    )

    result = runner.invoke(
        app,
        ["profile", "local-apply", "data"],
        env={"MSM_HOME": str(msm_home)},
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Deployed:" in result.output
