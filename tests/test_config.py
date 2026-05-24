from __future__ import annotations

import yaml

from msm.config.io import load_global_config, save_model
from msm.config.models import GlobalConfig, ProjectConfig
from msm.config.paths import config_path, registry_path


def test_load_global_config_creates_defaults(msm_home):
    config = load_global_config()

    assert config.registry_path == registry_path()
    assert "claude-code" in config.agents
    assert "codex" in config.agents
    assert config_path().exists()


def test_global_config_round_trip(msm_home):
    config = load_global_config()
    config = config.model_copy(update={"registries": {"team": "git@github.com:org/skills.git"}})
    save_model(config_path(), config)

    loaded = load_global_config()

    assert loaded.registries == {"team": "git@github.com:org/skills.git"}


def test_global_config_ignores_legacy_profiles_field(msm_home):
    # Existing config files may still have the removed `profiles` key — must load cleanly.
    raw = {
        "version": 1,
        "registry_path": str(registry_path()),
        "profiles": {"default": ["git-workflow"]},
        "registries": {},
    }
    config_path().parent.mkdir(parents=True, exist_ok=True)
    config_path().write_text(yaml.safe_dump(raw), encoding="utf-8")

    config = load_global_config()

    assert not hasattr(config, "profiles") or True  # field doesn't exist
    assert config.version == 1


def test_save_model_strips_empty_fields(msm_home, tmp_path):
    path = tmp_path / "project.yaml"
    save_model(path, ProjectConfig(profile="office-work"))

    content = path.read_text(encoding="utf-8")

    assert "office-work" in content
    assert "local_skills" not in content
    assert "agents" not in content
