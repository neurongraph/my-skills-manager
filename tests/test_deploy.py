from __future__ import annotations

from pathlib import Path

from msm.config.state import load_state
from msm.deploy.manager import DeploymentManager


def test_deploy_symlink_is_idempotent(msm_home, sample_skill, tmp_path: Path):
    target_dir = tmp_path / "target"
    deployer = DeploymentManager()

    first = deployer.deploy_skill("postgres-expert", sample_skill, target_dir, "codex", "global")
    second = deployer.deploy_skill("postgres-expert", sample_skill, target_dir, "codex", "global")

    assert first.changed is True
    assert second.changed is False
    assert (target_dir / "postgres-expert").is_symlink()
    assert len(load_state().deployments) == 1


def test_remove_deployment(msm_home, sample_skill, tmp_path: Path):
    target_dir = tmp_path / "target"
    deployer = DeploymentManager()
    deployer.deploy_skill("postgres-expert", sample_skill, target_dir, "codex", "global")

    removed = deployer.remove_skill("postgres-expert")

    assert removed == [target_dir / "postgres-expert"]
    assert not (target_dir / "postgres-expert").exists()

