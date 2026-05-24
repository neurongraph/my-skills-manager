from __future__ import annotations

from pathlib import Path

from msm.agents.adapters import enabled_adapters
from msm.config.io import load_global_config


def test_enabled_adapters_return_global_and_local_paths(msm_home, tmp_path):
    adapters = enabled_adapters(load_global_config())

    assert adapters["codex"].global_skill_path().is_absolute()
    assert adapters["codex"].local_skill_path(tmp_path) == tmp_path / ".codex" / "skills"

