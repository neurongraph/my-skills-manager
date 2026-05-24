from __future__ import annotations

from msm.config import paths
from msm.config.io import save_model
from msm.config.models import DeploymentRecord, DeploymentState


def load_state() -> DeploymentState:
    path = paths.state_path()
    if not path.exists():
        return DeploymentState()
    from msm.config.io import load_model

    return load_model(path, DeploymentState)


def save_state(state: DeploymentState) -> None:
    save_model(paths.state_path(), state)


def upsert_record(state: DeploymentState, record: DeploymentRecord) -> DeploymentState:
    remaining = [
        item
        for item in state.deployments
        if not (
            item.skill == record.skill
            and item.agent == record.agent
            and item.scope == record.scope
            and item.target == record.target
        )
    ]
    remaining.append(record)
    return DeploymentState(version=state.version, deployments=remaining)


def remove_records(state: DeploymentState, skill: str | None = None) -> DeploymentState:
    if skill is None:
        return DeploymentState(version=state.version)
    return DeploymentState(
        version=state.version,
        deployments=[item for item in state.deployments if item.skill != skill],
    )
