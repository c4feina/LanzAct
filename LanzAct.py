#!/usr/bin/env python3

import os
import sys
import json
import shutil
import platform
import argparse
import subprocess
from pathlib import Path

CONFIG_FILE = Path.home() / ".config" / "proyecto_lanzact" / "proyecto.json"

DEFAULT_CONFIG = {
    "example": {
        "editor": "code ~/example",
        "terminal": "~/example",
        "browser": ["https://github.com"]
    }
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        print(f"Connfig creada en {CONFIG_FILE}")
        print("Editar o agregar proyectos.")
        sys.exit(0)
    with open(CONFIG_FILE) as f:
        return json.load(f)


def open_editor(command: str):
    if not command:
        return
    system = platform.system()
    if system == "Windows":
        subprocess.Popen(command, shell=True)
    else:
        subprocess.Popen(command, shell=True)


def open_terminal(path: str):
    if not path:
        return
    expanded = os.path.expanduser(path)
    system = platform.system()

    if system == "Linux":
        terminal = (
            shutil.which("gnome-terminal") or
            shutil.which("konsole") or
            shutil.which("xterm") or
            shutil.which("alacritty") or
            shutil.which("kitty")
        )
        if not terminal:
            print("No emulacion de la terminal, verificar")
            return
        name = Path(terminal).name
        if name == "gnome-terminal":
            subprocess.Popen([terminal, "--working-directory", expanded])
        elif name in ("konsole", "alacritty", "kitty", "xterm"):
            subprocess.Popen([terminal, "--working-directory", expanded])
        else:
            subprocess.Popen([terminal])

    elif system == "Windows":
        subprocess.Popen(["wt", "-d", expanded], shell=True)

    elif system == "Darwin":
        script = f'app de "Terminal" para script "cd {expanded}"'
        subprocess.Popen(["osascript", "-e", script])


def open_browser(urls):
    if not urls:
        return
    if isinstance(urls, str):
        urls = [urls]
    system = platform.system()
    for url in urls:
        if system == "Linux":
            subprocess.Popen(["xdg-open", url])
        elif system == "Windows":
            subprocess.Popen(["start", url], shell=True)
        elif system == "Darwin":
            subprocess.Popen(["open", url])


def launch_project(name: str, config: dict):
    if name not in config:
        print(f"Project '{name}' not found.")
        print(f"Available: {', '.join(config.keys())}")
        sys.exit(1)

    project = config[name]
    print(f"Launching '{name}'...")

    if "editor" in project:
        open_editor(project["editor"])

    if "terminal" in project:
        open_terminal(project["terminal"])

    if "browser" in project:
        open_browser(project["browser"])


def list_projects(config: dict):
    print("Configurando proyectos:")
    for name, settings in config.items():
        parts = []
        if "editor" in settings:
            parts.append(f"editor: {settings['editor']}")
        if "terminal" in settings:
            parts.append(f"terminal: {settings['terminal']}")
        if "browser" in settings:
            urls = settings["browser"]
            if isinstance(urls, list):
                parts.append(f"browser: {len(urls)} url(s)")
            else:
                parts.append(f"browser: {urls}")
        print(f"  {name}: {' | '.join(parts)}")


def edit_config():
    editor = os.environ.get("EDITOR", "nano")
    subprocess.run([editor, str(CONFIG_FILE)])


def main():
    parser = argparse.ArgumentParser(
        description="Lanzact es un launcher para hacer un atajo de teclado y que te lanze las aplicaciones o cosas que quieras con tan solo 2 teclas"
    )
    parser.add_argument("proyecto", nargs="?", help="Lanzact o nombre de proyecto")
    parser.add_argument("--list", "-l", action="store_true", help="Listar todo")
    parser.add_argument("--edit", "-e", action="store_true", help="Edit config archivo")
    parser.add_argument("--config", "-c", action="store_true", help="Print config del path")

    args = parser.parse_args()

    if args.config:
        print(CONFIG_FILE)
        return

    if args.edit:
        edit_config()
        return

    config = load_config()

    if args.list:
        list_projects(config)
        return

    if not args.project:
        parser.print_help()
        print(f"\nAvailable projects: {', '.join(config.keys())}")
        return

    launch_project(args.project, config)


if __name__ == "__main__":
    main()