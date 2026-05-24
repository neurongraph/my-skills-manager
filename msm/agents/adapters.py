from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from msm.config.models import AgentConfig, GlobalConfig
from msm.config.paths import expand_path


@dataclass(frozen=True)
class AgentAdapter:
    name: str
    config: AgentConfig

    def global_skill_path(self) -> Path:
        return expand_path(self.config.global_path)

    def local_skill_path(self, project_root: Path) -> Path:
        return expand_path(self.config.local_path, project_root)

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.config.enabled:
            return issues
        if not self.config.global_path:
            issues.append(f"{self.name}: missing global_path")
        if not self.config.local_path:
            issues.append(f"{self.name}: missing local_path")
        return issues


def enabled_adapters(config: GlobalConfig) -> dict[str, AgentAdapter]:
    return {
        name: AgentAdapter(name, agent_config)
        for name, agent_config in config.agents.items()
        if agent_config.enabled
    }


def selected_adapters(config: GlobalConfig, agent: str | None = None) -> dict[str, AgentAdapter]:
    adapters = enabled_adapters(config)
    if agent is None:
        return adapters
    if agent not in adapters:
        raise ValueError(f"Agent is not enabled or configured: {agent}")
    return {agent: adapters[agent]}
