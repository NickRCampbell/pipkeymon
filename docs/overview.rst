Overview
========

PipKeyMon is a small Windows-only package that reads controller state with pygame and injects keyboard input with Win32 ``SendInput`` using scan codes.

It is intended for browser-based web games that accept keyboard input but do not understand controller input directly.

Key capabilities:

- Buttons to keys
- D-pad or hats to arrow keys
- Axes to digital keyboard directions
- Clean key release on shutdown
