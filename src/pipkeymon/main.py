import contextlib

from pipkeymon.config import load_config


def run_mapper(debug=False):
    from pipkeymon.input_reader import ControllerInputReader
    from pipkeymon.key_sender import KeySender

    config, config_path = load_config()
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
