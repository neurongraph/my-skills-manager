from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from msm.config.models import DeploymentRecord, DeploymentState
from msm.config.state import load_state, save_state, upsert_record


@dataclass(frozen=True)
class DeploymentResult:
    record: DeploymentRecord
    changed: bool


class DeploymentManager:
    def __init__(self, state: DeploymentState | None = None):
        self.state = state or load_state()

    def deploy_skill(
        self,
        skill: str,
        source: Path,
        target_dir: Path,
        agent: str,
        scope: str,
        mode: str = "symlink",
    ) -> DeploymentResult:
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / skill
        changed = self._materialize(source, target, mode)
        actual_mode = "symlink" if target.is_symlink() else "copy"
        record = DeploymentRecord(
            skill=skill,
            agent=agent,
            scope=scope,
            source=source,
            target=target,
            mode=actual_mode,
        )
        self.state = upsert_record(self.state, record)
        save_state(self.state)
        return DeploymentResult(record=record, changed=changed)

    def remove_skill(self, skill: str) -> list[Path]:
        removed: list[Path] = []
        kept = []
        for record in self.state.deployments:
            if record.skill != skill:
                kept.append(record)
                continue
            if record.target.is_symlink() or record.target.is_file():
                record.target.unlink(missing_ok=True)
                removed.append(record.target)
            elif record.target.exists():
                shutil.rmtree(record.target)
                removed.append(record.target)
        self.state = DeploymentState(version=self.state.version, deployments=kept)
        save_state(self.state)
        return removed

    def broken_symlinks(self) -> list[Path]:
        broken = []
        for record in self.state.deployments:
            if record.target.is_symlink() and not record.target.exists():
                broken.append(record.target)
        return broken

    def _materialize(self, source: Path, target: Path, mode: str) -> bool:
        if target.is_symlink() and target.resolve() == source.resolve():
            return False
        if target.exists() or target.is_symlink():
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        if mode == "symlink":
            try:
                target.symlink_to(source.resolve(), target_is_directory=True)
                return True
            except OSError:
                pass
        shutil.copytree(source, target, symlinks=True)
        return True
