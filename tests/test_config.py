from __future__ import annotations

from msm.config.io import load_global_config, save_model
from msm.config.models import GlobalConfig
from msm.config.paths import config_path, registry_path


def test_load_global_config_creates_defaults(msm_home):
    config = load_global_config()

    assert config.registry_path == registry_path()
    assert "claude-code" in config.agents
    assert "codex" in config.agents
    assert config_path().exists()


def test_global_config_round_trip(msm_home):
    config = load_global_config()
    config = config.model_copy(update={"profiles": {"default": ["git-workflow"]}})
    save_model(config_path(), config)

    loaded = GlobalConfig.model_validate(load_global_config().model_dump())

    assert loaded.profiles == {"default": ["git-workflow"]}

