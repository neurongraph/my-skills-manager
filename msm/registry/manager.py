from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from msm.config.io import load_model, save_model
from msm.config.models import GlobalConfig, SkillMetadata
from msm.config.paths import expand_path, remote_registries_path


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    source: str = "local"
    metadata: SkillMetadata | None = None


class RegistryManager:
    def __init__(self, config: GlobalConfig):
        self.config = config
        self.root = expand_path(config.registry_path)
        self.remote_root = remote_registries_path()

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def list_skills(self) -> list[Skill]:
        self.ensure()
        skills_by_name: dict[str, Skill] = {}
        for path in self._skill_dirs(self.root):
            skills_by_name[path.name] = Skill(path.name, path, "local", self.metadata_at(path))
        for registry_name, registry_path in self.remote_registry_paths():
            for path in self._skill_dirs(registry_path):
                skills_by_name.setdefault(
                    path.name,
                    Skill(path.name, path, registry_name, self.metadata_at(path)),
                )
        return [skills_by_name[name] for name in sorted(skills_by_name)]

    def resolve(self, name: str) -> Path:
        path = self.root / name
        if (path / "SKILL.md").exists():
            return path
        for _, registry_path in self.remote_registry_paths():
            path = registry_path / name
            if (path / "SKILL.md").exists():
                return path
        raise FileNotFoundError(f"Skill not found in registry: {name}")

    def metadata_for(self, name: str) -> SkillMetadata | None:
        return self.metadata_at(self.resolve(name))

    def metadata_at(self, skill_path: Path) -> SkillMetadata | None:
        path = skill_path / "metadata.yaml"
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
        return Skill(skill_name, target, "local", self.metadata_for(skill_name))

    def remove(self, name: str) -> None:
        path = self.root / name
        if path.exists() or path.is_symlink():
            shutil.rmtree(path)

    def save_registry_reference(self, name: str, url: str) -> GlobalConfig:
        if name in self.config.registries:
            raise ValueError(f"Registry already configured: {name}")
        self.clone_registry(name, url)
        registries = dict(self.config.registries)
        registries[name] = url
        return self.config.model_copy(update={"registries": registries})

    def update_external_registries(self) -> list[str]:
        messages: list[str] = []
        for name, url in sorted(self.config.registries.items()):
            target = self.remote_root / name
            if (target / ".git").exists():
                self._run_git(["git", "-C", str(target), "pull", "--ff-only"])
                messages.append(f"Updated {name}: {target}")
            else:
                self.clone_registry(name, url)
                messages.append(f"Cloned {name}: {target}")
        return messages

    def clone_registry(self, name: str, url: str) -> Path:
        target = self.remote_root / name
        if target.exists():
            if (target / ".git").exists():
                raise ValueError(f"Registry clone already exists: {target}")
            raise ValueError(f"Registry target exists and is not a Git repo: {target}")
        self.remote_root.mkdir(parents=True, exist_ok=True)
        self._run_git(["git", "clone", url, str(target)])
        return target

    def remote_registry_paths(self) -> list[tuple[str, Path]]:
        paths: list[tuple[str, Path]] = []
        for name in sorted(self.config.registries):
            path = self.remote_root / name
            if path.exists():
                paths.append((name, path))
        return paths

    def duplicate_skills(self) -> dict[str, list[str]]:
        sources: dict[str, list[str]] = {}
        for path in self._skill_dirs(self.root):
            sources.setdefault(path.name, []).append("local")
        for registry_name, registry_path in self.remote_registry_paths():
            for path in self._skill_dirs(registry_path):
                sources.setdefault(path.name, []).append(registry_name)
        return {
            skill: skill_sources
            for skill, skill_sources in sorted(sources.items())
            if len(skill_sources) > 1
        }

    def missing_remote_clones(self) -> list[str]:
        return [
            name
            for name in sorted(self.config.registries)
            if not (self.remote_root / name / ".git").exists()
        ]

    def _skill_dirs(self, root: Path) -> list[Path]:
        if not root.exists():
            return []
        return [
            item
            for item in sorted(root.iterdir())
            if item.is_dir() and (item / "SKILL.md").exists()
        ]

    def _run_git(self, command: list[str]) -> None:
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise RuntimeError("Git is required for remote registries") from exc
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() or exc.stdout.strip()
            raise RuntimeError(f"Git command failed: {stderr}") from exc


def write_skill_metadata(path: Path, metadata: SkillMetadata) -> None:
    save_model(path / "metadata.yaml", metadata)
