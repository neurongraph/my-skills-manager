from __future__ import annotations

from pathlib import Path

from msm.agents.adapters import AgentAdapter, enabled_adapters, selected_adapters
from msm.config import paths
from msm.config.io import load_global_config, load_model, save_model
from msm.config.models import ExportConfig, ExportMachine, GlobalConfig, ProfileConfig, ProjectConfig
from msm.config.state import load_state
from msm.deploy.manager import DeploymentManager
from msm.registry.manager import RegistryManager, Skill


class MSMService:
    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.config = load_global_config()
        self.registry = RegistryManager(self.config)

    def skill_list(self) -> list[Skill]:
        return self.registry.list_skills()

    def skill_add(
        self,
        name: str,
        source: Path | None = None,
        global_scope: bool = True,
        local_scope: bool = False,
        agent: str | None = None,
    ) -> list[str]:
        if source is not None:
            self.registry.install_from_path(source, name)
        skill_path = self.registry.resolve(name)
        adapters = selected_adapters(self.config, agent)
        messages: list[str] = []
        deployer = DeploymentManager()
        for adapter_name, adapter in adapters.items():
            if global_scope:
                result = deployer.deploy_skill(
                    name,
                    skill_path,
                    adapter.global_skill_path(),
                    adapter_name,
                    "global",
                    self.config.default_deployment_mode,
                )
                messages.append(self._deploy_message(result.record.target, result.changed))
            if local_scope:
                result = deployer.deploy_skill(
                    name,
                    skill_path,
                    adapter.local_skill_path(self.project_root),
                    adapter_name,
                    "local",
                    self.config.default_deployment_mode,
                )
                messages.append(self._deploy_message(result.record.target, result.changed))
        return messages

    def skill_remove(self, name: str) -> list[str]:
        removed = DeploymentManager().remove_skill(name)
        self.registry.remove(name)
        messages = [f"Removed deployment: {path}" for path in removed]
        messages.append(f"Removed registry skill: {name}")
        return messages

    def profile_list(self) -> list[str]:
        profile_dir = paths.profiles_path()
        if not profile_dir.exists():
            return []
        return sorted(path.stem for path in profile_dir.glob("*.yaml"))

    def profile_path(self, name: str) -> Path:
        return paths.profiles_path() / f"{name}.yaml"

    def load_profile(self, name: str) -> ProfileConfig:
        path = self.profile_path(name)
        if not path.exists():
            raise FileNotFoundError(f"Profile not found: {name}")
        return load_model(path, ProfileConfig)

    def profile_validate(self, name: str) -> list[str]:
        profile = self.load_profile(name)
        issues: list[str] = []
        for skill in self._profile_skill_names(profile):
            try:
                self.registry.resolve(skill)
            except FileNotFoundError:
                issues.append(f"Missing skill: {skill}")
        for agent in profile.agents:
            if agent not in self.config.agents:
                issues.append(f"Unknown agent: {agent}")
        return issues

    def profile_apply_global(self, name: str) -> list[str]:
        issues = self.profile_validate(name)
        if issues:
            raise ValueError("; ".join(issues))
        profile = self.load_profile(name)
        return self._deploy_profile(profile, "global")

    def profile_apply_local(self, name: str) -> list[str]:
        issues = self.profile_validate(name)
        if issues:
            raise ValueError("; ".join(issues))
        profile = self.load_profile(name)
        project_path = paths.project_config_path(self.project_root)
        project = load_model(project_path, ProjectConfig) if project_path.exists() else ProjectConfig()
        project.profile = name
        save_model(project_path, project)
        return self._deploy_profile(profile, "local")

    def _deploy_profile(self, profile: ProfileConfig, scope: str) -> list[str]:
        messages: list[str] = []
        adapters = enabled_adapters(self.config)
        for skill in profile.global_skills:
            for adapter_name, adapter in adapters.items():
                messages.extend(self._deploy_to_adapter(skill, adapter_name, adapter, scope))
        for adapter_name, entry in profile.agents.items():
            adapter = adapters.get(adapter_name)
            if adapter is None:
                continue
            for skill in entry.get("skills", []):
                messages.extend(self._deploy_to_adapter(skill, adapter_name, adapter, scope))
        return messages

    def sync(self) -> list[str]:
        messages: list[str] = []
        project_path = paths.project_config_path(self.project_root)
        if project_path.exists():
            project = load_model(project_path, ProjectConfig)
            if project.profile:
                messages.extend(self.profile_apply_local(project.profile))
            adapters = enabled_adapters(self.config)
            for skill in project.local_skills:
                for adapter_name, adapter in adapters.items():
                    messages.extend(self._deploy_to_adapter(skill, adapter_name, adapter, "local"))
            for adapter_name, entry in project.agents.items():
                adapter = adapters.get(adapter_name)
                if adapter is None:
                    continue
                for skill in entry.get("additional_skills", []):
                    messages.extend(self._deploy_to_adapter(skill, adapter_name, adapter, "local"))
        return messages or ["Environment already in sync"]

    def doctor(self) -> list[str]:
        issues: list[str] = []
        try:
            config = load_global_config(create=False)
        except Exception as exc:
            return [f"Invalid global config: {exc}"]
        for name, adapter_config in config.agents.items():
            issues.extend(AgentAdapter(name, adapter_config).validate())
        registry = RegistryManager(config)
        for name in registry.missing_remote_clones():
            issues.append(f"Missing remote registry clone: {name}")
        for skill, sources in registry.duplicate_skills().items():
            issues.append(f"Duplicate skill '{skill}' found in: {', '.join(sources)}")
        for record in load_state().deployments:
            if not record.source.exists():
                issues.append(f"Missing deployed skill source: {record.skill} -> {record.source}")
            if record.target.is_symlink() and not record.target.exists():
                issues.append(f"Broken symlink: {record.target}")
        return issues or ["No issues found"]

    def export(self) -> ExportConfig:
        state = load_state()
        profiles = {name: self.load_profile(name) for name in self.profile_list()}
        skills = sorted({record.skill for record in state.deployments})
        agents = sorted({record.agent for record in state.deployments})
        return ExportConfig(machine=ExportMachine(
            profiles=profiles,
            deployed_skills=skills,
            agents=agents,
            registries=dict(self.config.registries),
        ))

    def import_file(self, path: Path) -> list[str]:
        export = load_model(path, ExportConfig)
        messages: list[str] = []
        for name, profile_config in export.machine.profiles.items():
            profile_path = paths.profiles_path() / f"{name}.yaml"
            save_model(profile_path, profile_config)
            messages.append(f"Imported profile: {name}")
        for name, url in export.machine.registries.items():
            if name in self.config.registries:
                messages.append(f"Registry already configured, skipping: {name}")
                continue
            try:
                messages.append(self.registry_add(name, url))
            except ValueError as exc:
                messages.append(f"Warning: could not add registry {name}: {exc}")
        if export.machine.registries:
            try:
                messages.extend(self.registry_update())
            except ValueError as exc:
                messages.append(f"Warning: registry update failed: {exc}")
        for skill in export.machine.deployed_skills:
            messages.extend(self.skill_add(skill))
        return messages or ["Nothing to import"]

    def registry_add(self, name: str, url: str) -> str:
        try:
            self.config = self.registry.save_registry_reference(name, url)
        except (RuntimeError, ValueError) as exc:
            raise ValueError(str(exc)) from exc
        save_model(paths.config_path(), self.config)
        return f"Registered and cloned {name}: {url}"

    def registry_update(self) -> list[str]:
        try:
            updates = self.registry.update_external_registries()
        except RuntimeError as exc:
            raise ValueError(str(exc)) from exc
        return updates or ["No external registries configured"]

    def init_project(self, profile: str | None = None) -> Path:
        path = paths.project_config_path(self.project_root)
        config = ProjectConfig(profile=profile)
        save_model(path, config)
        (self.project_root / ".msm" / "deployed").mkdir(parents=True, exist_ok=True)
        return path

    def _profile_skill_names(self, profile: ProfileConfig) -> set[str]:
        names = set(profile.global_skills)
        for entry in profile.agents.values():
            names.update(entry.get("skills", []))
        return names

    def _deploy_to_adapter(
        self, skill: str, adapter_name: str, adapter: AgentAdapter, scope: str
    ) -> list[str]:
        source = self.registry.resolve(skill)
        target_dir = (
            adapter.global_skill_path()
            if scope == "global"
            else adapter.local_skill_path(self.project_root)
        )
        result = DeploymentManager().deploy_skill(
            skill,
            source,
            target_dir,
            adapter_name,
            scope,
            self.config.default_deployment_mode,
        )
        return [self._deploy_message(result.record.target, result.changed)]

    def _deploy_message(self, target: Path, changed: bool) -> str:
        action = "Deployed" if changed else "Unchanged"
        return f"{action}: {target}"
