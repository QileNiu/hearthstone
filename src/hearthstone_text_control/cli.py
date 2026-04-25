from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path

from .backends import DryRunBackend, PyAutoGuiBackend
from .config import load_default_profile, load_profile
from .engine import CommandEngine


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    profile = load_profile(args.profile) if args.profile else load_default_profile()
    backend = PyAutoGuiBackend() if args.live else DryRunBackend()
    engine = CommandEngine(profile, backend)

    commands = list(_iter_commands(args))
    if commands:
        for command in commands:
            result = engine.execute(command)
            if result.message:
                print(result.message)
            if result.should_exit:
                break
        return 0

    mode = "LIVE" if args.live else "DRY-RUN"
    print(f"Hearthstone text control loaded profile '{profile.name}' in {mode} mode.")
    print("Type 帮助 for commands, 退出 to quit.")
    while True:
        try:
            line = input("> ")
        except EOFError:
            print()
            return 0
        result = engine.execute(line)
        if result.message:
            print(result.message)
        if result.should_exit:
            return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Text-command accessibility controller for Hearthstone."
    )
    parser.add_argument(
        "--profile",
        help="Path to a JSON coordinate profile. Uses the bundled example profile if omitted.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute real mouse actions with pyautogui. Default is dry-run.",
    )
    parser.add_argument(
        "--command",
        action="append",
        default=[],
        help="Command to execute. Can be provided multiple times.",
    )
    parser.add_argument(
        "--script",
        help="UTF-8 text file containing one command per line.",
    )
    return parser.parse_args(argv)


def _iter_commands(args: argparse.Namespace) -> Iterable[str]:
    for command in args.command:
        yield command
    if args.script:
        script_path = Path(args.script)
        with script_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                command = line.strip()
                if command and not command.startswith("#"):
                    yield command


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
