from __future__ import annotations

import pytest

from msm.config.io import load_global_config
from msm.registry.manager import RegistryManager


def test_registry_install_list_resolve_and_remove(msm_home, sample_skill):
    registry = RegistryManager(load_global_config())

    installed = registry.install_from_path(sample_skill)

    assert installed.name == "postgres-expert"
    assert registry.resolve("postgres-expert").name == "postgres-expert"
    assert registry.list_skills()[0].name == "postgres-expert"

    registry.remove("postgres-expert")

    with pytest.raises(FileNotFoundError):
        registry.resolve("postgres-expert")

