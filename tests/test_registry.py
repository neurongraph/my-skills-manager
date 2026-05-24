from __future__ import annotations

import subprocess

import pytest

from msm.config.io import load_global_config
from msm.config.paths import remote_registries_path
from msm.registry.manager import RegistryManager


def run_git(repo, *args: str) -> None:
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


def test_registry_install_list_resolve_and_remove(msm_home, sample_skill):
    registry = RegistryManager(load_global_config())

    installed = registry.install_from_path(sample_skill)

    assert installed.name == "postgres-expert"
    assert registry.resolve("postgres-expert").name == "postgres-expert"
    assert registry.list_skills()[0].name == "postgres-expert"

    registry.remove("postgres-expert")

    with pytest.raises(FileNotFoundError):
        registry.resolve("postgres-expert")


def test_remote_registry_add_clone_list_and_resolve(msm_home, remote_registry_repo):
    registry = RegistryManager(load_global_config())

    updated_config = registry.save_registry_reference("team", str(remote_registry_repo))
    registry = RegistryManager(updated_config)
    skills = registry.list_skills()

    assert (remote_registries_path() / "team" / ".git").exists()
    assert skills[0].name == "spark-scala"
    assert skills[0].source == "team"
    assert skills[0].metadata is not None
    assert skills[0].metadata.description == "Spark engineering with Scala"
    assert registry.resolve("spark-scala") == remote_registries_path() / "team" / "spark-scala"


def test_remote_registry_update_pulls_new_skills(msm_home, remote_registry_repo):
    registry = RegistryManager(load_global_config())
    config = registry.save_registry_reference("team", str(remote_registry_repo))
    new_skill = remote_registry_repo / "python-refactor"
    new_skill.mkdir()
    (new_skill / "SKILL.md").write_text("# Python Refactor\n", encoding="utf-8")
    (new_skill / "metadata.yaml").write_text(
        "name: python-refactor\ndescription: Python refactoring support\n",
        encoding="utf-8",
    )
    run_git(remote_registry_repo, "add", ".")
    run_git(remote_registry_repo, "commit", "-m", "add python refactor")

    messages = RegistryManager(config).update_external_registries()
    skills = {skill.name for skill in RegistryManager(config).list_skills()}

    assert messages == [f"Updated team: {remote_registries_path() / 'team'}"]
    assert "python-refactor" in skills


def test_local_registry_wins_over_remote_duplicate(msm_home, sample_skill, tmp_path):
    remote = tmp_path / "remote"
    remote.mkdir()
    subprocess_result = subprocess.run(["git", "init", str(remote)], check=True, capture_output=True, text=True)
    assert subprocess_result.returncode == 0
    duplicate = remote / "postgres-expert"
    duplicate.mkdir()
    (duplicate / "SKILL.md").write_text("# Remote Postgres\n", encoding="utf-8")
    (duplicate / "metadata.yaml").write_text(
        "name: postgres-expert\ndescription: Remote postgres skill\n",
        encoding="utf-8",
    )
    run_git(remote, "add", ".")
    run_git(remote, "commit", "-m", "add duplicate")

    registry = RegistryManager(load_global_config())
    config = registry.save_registry_reference("team", str(remote))
    registry = RegistryManager(config)
    registry.install_from_path(sample_skill)
    skill = registry.list_skills()[0]

    assert skill.name == "postgres-expert"
    assert skill.source == "local"
    assert registry.duplicate_skills() == {"postgres-expert": ["local", "team"]}
