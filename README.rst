PipKeyMon
=========

PipKeyMon is a small Windows-only Python package that reads a game controller with pygame and injects real keyboard input with Win32 ``SendInput``. It is aimed at browser-based games that only understand keyboard input.

Features
========

- Controller buttons to keyboard keys
- Controller buttons to arrow keys
- D-pad or hat input to arrow keys
- Joystick axes to digital keys using thresholds
- Press and release handling
- Clean release of held keys on shutdown
- CLI entry point and ``python -m`` support
- Human-editable JSON config that is auto-created on first run

Windows Only
============

This package only supports Windows because it injects keyboard input through Win32 ``SendInput`` with scan-code-based events.

Quick Start
===========

Open a terminal and run exactly:

.. code-block:: powershell

   cd C:\ControlerKeysMapper
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -e .
   pipkeymon --help
   pipkeymon run

If you need to inspect controller input while setting up mappings, use debug mode after the normal run path is working:

.. code-block:: powershell

   pipkeymon run --debug

The same commands also work with ``python -m``:

.. code-block:: powershell

   cd C:\ControlerKeysMapper
   .venv\Scripts\activate
   python -m pipkeymon --help
   python -m pipkeymon run

Editable Install
================

For normal development:

.. code-block:: powershell

   cd C:\ControlerKeysMapper
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -e .

If you want to build the Sphinx docs too:

.. code-block:: powershell

   pip install -e .[docs]

How To Run
==========

Normal mode:

.. code-block:: powershell

   pipkeymon run

Debug mode:

.. code-block:: powershell

   pipkeymon run --debug

Or:

.. code-block:: powershell

   python -m pipkeymon run --debug

Config Location
===============

The config file is created automatically on first run at:

.. code-block:: text

   %LOCALAPPDATA%\PipKeyMon\config.json

You can print the path:

.. code-block:: powershell

   pipkeymon config-path

You can open it in your default editor:

.. code-block:: powershell

   pipkeymon edit-config

Default Mapping
===============

The default JSON config maps:

- Button ``0`` to ``SPACE``
- Button ``1`` to ``ESCAPE``
- Hat ``0`` to arrow keys
- Axis ``0`` to ``A`` and ``D``
- Axis ``1`` to ``W`` and ``S``

Some controllers expose the d-pad as a hat, and some expose it as ordinary buttons. During validation on a DualSense in this environment, pygame reported zero hats, so d-pad directions may need to be mapped through ``button_map`` after a short debug run.

Example config:

.. code-block:: json

   {
     "selected_controller_index": 0,
     "poll_interval_ms": 8,
       "axis_deadzone": 0.12,
     "button_map": {
       "0": "SPACE",
       "1": "ESCAPE"
     },
     "hat_map": {
       "0": {
         "up": "UP",
         "down": "DOWN",
         "left": "LEFT",
         "right": "RIGHT"
       }
     },
     "axis_map": {
       "0": {
         "negative": "A",
         "positive": "D",
         "threshold": 0.5
       },
       "1": {
         "negative": "W",
         "positive": "S",
         "threshold": 0.5
       }
     }
   }

``axis_deadzone`` clamps small stick jitter back to zero before threshold handling. You can also set ``deadzone`` inside an individual axis mapping to override the global default for that axis.

Typical After-Work Flow
=======================

.. code-block:: powershell

   cd C:\ControlerKeysMapper
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -e .
   pipkeymon --help
   pipkeymon run --debug
   pipkeymon edit-config
   pipkeymon run

Then open your browser, navigate to the game, and play.

Known Limitations
=================

- Windows only
- No GUI
- No profile manager
- No rumble or controller feedback
- Default controller button numbering depends on how pygame reports the device
- Some controllers report the d-pad as buttons instead of a hat, so the config may need a quick debug-driven adjustment
- Only one selected controller is read at a time
- Axis mapping is digital threshold-based rather than analog

Documentation
=============

Sphinx docs live under ``docs/``.

Build them with:

.. code-block:: powershell

   pip install -e .[docs]
   sphinx-build -b html docs docs/_build/html

Release Process
===============

For the next release:

.. code-block:: powershell

   git add .
   git commit -m "Release X.Y.Z"
   git push
   python -m build
   python -m twine check dist/*
   python -m twine upload dist/*

Bump the version in ``pyproject.toml`` and ``src/pipkeymon/__init__.py`` before uploading a new release.
