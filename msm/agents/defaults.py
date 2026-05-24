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
            global_path=Path("~/.codex/skills"),
            local_path=Path(".codex/skills"),
        ),
        "antigravity": AgentConfig(
            enabled=True,
            global_path=Path("~/.gemini/antigravity/skills"),
            local_path=Path(".agents/skills"),
        ),
        "opencode": AgentConfig(
            enabled=True,
            global_path=Path("~/.agents/skills"),
            local_path=Path(".agents/skills"),
        ),
        "bob": AgentConfig(
            enabled=True,
            global_path=Path("~/.bob/skills"),
            local_path=Path(".bob/skills"),
        ),
        "pi": AgentConfig(
            enabled=True,
            global_path=Path("~/.agents/skills"),
            local_path=Path(".agents/skills"),
        ),
    }

