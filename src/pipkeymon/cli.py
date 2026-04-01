import argparse
import os
import sys

from pipkeymon.config import ensure_config_exists
from pipkeymon.main import run_mapper


def build_parser():
    parser = argparse.ArgumentParser(
        prog="pipkeymon",
        description="Map a controller to real keyboard input for browser-based games on Windows.",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Start the controller to keyboard mapping loop")
    run_parser.add_argument("--debug", action="store_true", help="Print controller activity and mapped key actions")

    subparsers.add_parser("config-path", help="Print the JSON config path")
    subparsers.add_parser("edit-config", help="Open the JSON config in the system default editor")

    parser.add_argument("--debug", action="store_true", help="Print controller activity and mapped key actions")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command or "run"

    if command == "config-path":
        config_path = ensure_config_exists()
        print(config_path)
        return 0

    if command == "edit-config":
        config_path = ensure_config_exists()
        print(f"Config path: {config_path}")
        os.startfile(str(config_path))
        return 0

    debug = bool(getattr(args, "debug", False))
    run_mapper(debug=debug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
