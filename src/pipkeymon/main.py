import contextlib

from pipkeymon import __github_url__, __version__
from pipkeymon.config import load_config


BANNER = r"""
 ____  _       _  __         __  __
|  _ \(_)_ __ | |/ /___ _   |  \/  | ___  _ __
| |_) | | '_ \| ' // _ \ | | | |\/| |/ _ \| '_ \
|  __/| | |_) | . \  __/ |_| | |  | | (_) | | | |
|_|   |_| .__/|_|\_\___|\__, |_|  |_|\___/|_| |_|
        |_|             |___/
""".strip("\n")


def print_startup_banner():
    print(BANNER)
    print(f"Version: {__version__} - GitHub: {__github_url__}")
    print()


def run_mapper(debug=False):
    from pipkeymon.input_reader import ControllerInputReader
    from pipkeymon.key_sender import KeySender

    config, config_path = load_config()
    print_startup_banner()
    print(f"Config path: {config_path}")
    sender = KeySender(debug=debug)
    reader = ControllerInputReader(config=config, sender=sender, debug=debug)
    reader.setup()
    try:
        reader.run_forever()
    except KeyboardInterrupt:
        print("Interrupted; releasing held keys and exiting")
    finally:
        with contextlib.suppress(Exception):
            reader.shutdown()
