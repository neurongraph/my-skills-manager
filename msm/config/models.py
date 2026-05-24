from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    global_path: Path
    local_path: Path


class GlobalConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version: int = 1
    registry_path: Path = Path("~/.msm/registry")
    default_deployment_mode: str = "symlink"
    agents: dict[str, AgentConfig] = Field(default_factory=dict)
    registries: dict[str, str] = Field(default_factory=dict)


class ProfileConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str = ""
    global_skills: list[str] = Field(default_factory=list)
    agents: dict[str, dict[str, list[str]]] = Field(default_factory=dict)


class ProjectConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: str | None = None
    local_skills: list[str] = Field(default_factory=list)
    agents: dict[str, dict[str, list[str]]] = Field(default_factory=dict)


class SkillMetadata(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    description: str = ""
    version: str = "0.1.0"
    tags: list[str] = Field(default_factory=list)


class ExportMachine(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profiles: dict[str, ProfileConfig] = Field(default_factory=dict)
    deployed_skills: list[str] = Field(default_factory=list)
    agents: list[str] = Field(default_factory=list)
    registries: dict[str, str] = Field(default_factory=dict)


class ExportConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = 1
    machine: ExportMachine = Field(default_factory=ExportMachine)


class DeploymentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill: str
    agent: str
    scope: str
    source: Path
    target: Path
    mode: str


class DeploymentState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = 1
    deployments: list[DeploymentRecord] = Field(default_factory=list)

