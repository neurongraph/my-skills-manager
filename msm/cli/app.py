from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
import yaml
from rich.console import Console
from rich.table import Table

from msm import __version__
from msm.core.service import MSMService

app = typer.Typer(help="Portable AI coding environment manager.")
skill_app = typer.Typer(help="Manage skills.")
profile_app = typer.Typer(help="Manage profiles.")
registry_app = typer.Typer(help="Manage registries.")
init_app = typer.Typer(help="Initialize MSM project files.")

app.add_typer(skill_app, name="skill")
app.add_typer(profile_app, name="profile")
app.add_typer(registry_app, name="registry")
app.add_typer(init_app, name="init")

console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"msm {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", callback=version_callback, help="Show version and exit."),
    ] = None,
) -> None:
    return None


@skill_app.command("add")
def skill_add(
    name: str,
    source: Annotated[Path | None, typer.Option("--from", help="Install skill from a local directory first.")] = None,
    global_scope: Annotated[bool, typer.Option("--global", help="Deploy to global agent paths.")] = False,
    local_scope: Annotated[bool, typer.Option("--local", help="Deploy to project-local agent paths.")] = False,
    agent: Annotated[str | None, typer.Option("--agent", help="Deploy to one configured agent.")] = None,
) -> None:
    if not global_scope and not local_scope:
        global_scope = True
    _print_lines(MSMService().skill_add(name, source, global_scope, local_scope, agent))


@skill_app.command("remove")
def skill_remove(name: str) -> None:
    _print_lines(MSMService().skill_remove(name))


@skill_app.command("list")
def skill_list() -> None:
    skills = MSMService().skill_list()
    table = Table("Skill", "Description", "Source")
    for item in skills:
        description = item.metadata.description if item.metadata else ""
        table.add_row(item.name, description, item.source)
    console.print(table)


@profile_app.command("global-apply")
def profile_global_apply(name: str) -> None:
    try:
        _print_lines(MSMService().profile_apply_global(name))
    except (FileNotFoundError, ValueError) as exc:
        _fail(str(exc))


@profile_app.command("local-apply")
def profile_local_apply(name: str) -> None:
    try:
        _print_lines(MSMService().profile_apply_local(name))
    except (FileNotFoundError, ValueError) as exc:
        _fail(str(exc))


@profile_app.command("list")
def profile_list() -> None:
    profiles = MSMService().profile_list()
    table = Table("Profile")
    for item in profiles:
        table.add_row(item)
    console.print(table)


@profile_app.command("validate")
def profile_validate(name: str) -> None:
    try:
        issues = MSMService().profile_validate(name)
    except FileNotFoundError as exc:
        _fail(str(exc))
    if issues:
        _print_lines(issues)
        raise typer.Exit(1)
    console.print("Profile is valid")


@app.command("sync")
def sync() -> None:
    _print_lines(MSMService().sync())


@app.command("doctor")
def doctor() -> None:
    issues = MSMService().doctor()
    _print_lines(issues)
    if issues != ["No issues found"]:
        raise typer.Exit(1)


@app.command("export")
def export() -> None:
    payload = MSMService().export().model_dump(mode="json")
    console.print(yaml.safe_dump(payload, sort_keys=False), end="")


@app.command("import")
def import_cmd(path: Path) -> None:
    _print_lines(MSMService().import_file(path))


@registry_app.command("add")
def registry_add(name: str, url: str) -> None:
    try:
        console.print(MSMService().registry_add(name, url))
    except ValueError as exc:
        _fail(str(exc))


@registry_app.command("update")
def registry_update() -> None:
    try:
        _print_lines(MSMService().registry_update())
    except ValueError as exc:
        _fail(str(exc))


@init_app.command("project")
def init_project(profile: str | None = None) -> None:
    path = MSMService().init_project(profile)
    console.print(f"Created {path}")


def _print_lines(lines: list[str]) -> None:
    for line in lines:
        console.print(line)


def _fail(message: str) -> None:
    console.print(f"Error: {message}", style="red")
    raise typer.Exit(1)
