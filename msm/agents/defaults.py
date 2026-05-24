from __future__ import annotations

from pathlib import Path

from msm.config.models import AgentConfig


def default_agent_configs() -> dict[str, AgentConfig]:
    return {
        "claude-code": AgentConfig(
            enabled=True,
            global_path=Path("~/.claude/skills"),
            local_path=Path(".claude/skills"),
        ),
        "codex": AgentConfig(
            enabled=True,
            global_path=Path("~/.config/codex/skills"),
            local_path=Path(".codex/skills"),
        ),
    }

