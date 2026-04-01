Configuration
=============

The package stores a human-editable JSON config under ``%LOCALAPPDATA%\PipKeyMon\config.json``.

If the config file does not exist, it is created automatically on first run or when you ask for the config path.

Commands:

.. code-block:: powershell

  pipkeymon config-path
  pipkeymon edit-config

Main config fields:

- ``selected_controller_index``
- ``poll_interval_ms``
- ``axis_deadzone``
- ``button_map``
- ``hat_map``
- ``axis_map``

On some controllers, including some DualSense setups, pygame reports the d-pad as ordinary buttons instead of a hat. In that case, run debug mode, press each d-pad direction, note the button numbers that print, and map those button indices in ``button_map`` to ``UP``, ``DOWN``, ``LEFT``, and ``RIGHT``.

Axis mappings use a threshold and digital directions. Example:

.. code-block:: json

   "axis_map": {
     "0": {
       "negative": "A",
       "positive": "D",
       "threshold": 0.5
     }
   }

``axis_deadzone`` clamps small stick jitter back to zero before threshold processing. You can also set ``deadzone`` inside an individual axis mapping to override the global default for that axis.
