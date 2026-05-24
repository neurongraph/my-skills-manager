from __future__ import annotations

import os
from pathlib import Path


def msm_home() -> Path:
    return Path(os.environ.get("MSM_HOME", "~/.msm")).expanduser()


def config_path() -> Path:
    return msm_home() / "config.yaml"


def registry_path() -> Path:
    return msm_home() / "registry"


def remote_registries_path() -> Path:
    return msm_home() / "registries"


def profiles_path() -> Path:
    return msm_home() / "profiles"


def state_path() -> Path:
    return msm_home() / "state" / "deployments.yaml"


def project_config_path(project_root: Path | None = None) -> Path:
    root = project_root or Path.cwd()
    return root / ".msm" / "project.yaml"


def expand_path(path: Path, project_root: Path | None = None) -> Path:
    expanded = Path(path).expanduser()
    if not expanded.is_absolute() and project_root is not None:
        return project_root / expanded
    return expanded
