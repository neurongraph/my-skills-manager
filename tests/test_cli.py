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


def test_cli_doctor_clean(msm_home):
    result = runner.invoke(app, ["doctor"], env={"MSM_HOME": str(msm_home)})

    assert result.exit_code == 0
    assert "No issues found" in result.output
