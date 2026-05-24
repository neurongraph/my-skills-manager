from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from msm.config.io import load_model, save_model
from msm.config.models import GlobalConfig, SkillMetadata
from msm.config.paths import expand_path


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    metadata: SkillMetadata | None = None


class RegistryManager:
    def __init__(self, config: GlobalConfig):
        self.config = config
        self.root = expand_path(config.registry_path)

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def list_skills(self) -> list[Skill]:
        self.ensure()
        skills: list[Skill] = []
        for path in sorted(item for item in self.root.iterdir() if item.is_dir()):
            if (path / "SKILL.md").exists():
                skills.append(Skill(path.name, path, self.metadata_for(path.name)))
        return skills

    def resolve(self, name: str) -> Path:
        path = self.root / name
        if not (path / "SKILL.md").exists():
            raise FileNotFoundError(f"Skill not found in registry: {name}")
        return path

    def metadata_for(self, name: str) -> SkillMetadata | None:
        path = self.root / name / "metadata.yaml"
        if not path.exists():
            return None
        return load_model(path, SkillMetadata)

    def install_from_path(self, source: Path, name: str | None = None) -> Skill:
        source = source.expanduser().resolve()
        if not (source / "SKILL.md").exists():
            raise ValueError(f"Source skill must contain SKILL.md: {source}")
        skill_name = name or source.name
        target = self.root / skill_name
        self.ensure()
        if target.exists() or target.is_symlink():
            shutil.rmtree(target)
        shutil.copytree(source, target, symlinks=True)
        return Skill(skill_name, target, self.metadata_for(skill_name))

    def remove(self, name: str) -> None:
        path = self.root / name
        if path.exists() or path.is_symlink():
            shutil.rmtree(path)

    def save_registry_reference(self, name: str, url: str) -> GlobalConfig:
        registries = dict(self.config.registries)
        registries[name] = url
        return self.config.model_copy(update={"registries": registries})

    def update_external_registries(self) -> list[str]:
        return [f"{name}: {url}" for name, url in sorted(self.config.registries.items())]


def write_skill_metadata(path: Path, metadata: SkillMetadata) -> None:
    save_model(path / "metadata.yaml", metadata)
