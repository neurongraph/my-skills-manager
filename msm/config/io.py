from __future__ import annotations

from pathlib import Path
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel

from msm.agents.defaults import default_agent_configs
from msm.config import paths
from msm.config.models import GlobalConfig

ModelT = TypeVar("ModelT", bound=BaseModel)


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def _strip_empty(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: _strip_empty(v) for k, v in data.items() if v is not None and v != [] and v != {}}
    if isinstance(data, list):
        return [_strip_empty(v) for v in data]
    return data


def write_yaml(path: Path, data: BaseModel | dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = data.model_dump(mode="json") if isinstance(data, BaseModel) else data
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(_strip_empty(payload), handle, sort_keys=False)


def load_model(path: Path, model: type[ModelT]) -> ModelT:
    return model.model_validate(read_yaml(path))


def save_model(path: Path, value: BaseModel) -> None:
    write_yaml(path, value)


def default_global_config() -> GlobalConfig:
    return GlobalConfig(
        registry_path=paths.registry_path(),
        agents=default_agent_configs(),
    )


def load_global_config(create: bool = True) -> GlobalConfig:
    path = paths.config_path()
    if not path.exists():
        config = default_global_config()
        if create:
            save_model(path, config)
        return config
    data = read_yaml(path)
    if "agents" not in data or not data["agents"]:
        data["agents"] = default_agent_configs()
    if "registry_path" not in data:
        data["registry_path"] = paths.registry_path()
    return GlobalConfig.model_validate(data)

