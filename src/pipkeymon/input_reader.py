import time

import pygame


class ControllerInputReader:
    def __init__(self, config, sender, debug=False):
        self.config = config
        self.sender = sender
        self.debug = debug
        self.button_state = {}
        self.hat_state = {}
        self.axis_state = {}
        self.axis_raw_values = {}
        self.warned_no_controller = False
        self.warned_missing_buttons = set()
        self.warned_missing_hats = set()
        self.warned_missing_axes = set()
        self.joystick = None
        self.joystick_instance_id = None

    def _get_axis_deadzone(self, mapping):
        if "deadzone" in mapping:
            return float(mapping.get("deadzone", 0.12))
        return float(self.config.get("axis_deadzone", 0.12))

    def _apply_axis_deadzone(self, value, deadzone):
        if abs(value) < deadzone:
            return 0.0
        return value

    def setup(self):
        pygame.init()
        pygame.joystick.init()

    def shutdown(self):
        self.sender.release_all()
        if self.joystick is not None:
            self.joystick.quit()
        pygame.joystick.quit()
        pygame.quit()

    def run_forever(self):
        poll_interval_ms = int(self.config.get("poll_interval_ms", 8))
        selected_index = int(self.config.get("selected_controller_index", 0))
        while True:
            pygame.event.pump()
            self._ensure_joystick(selected_index)
            if self.joystick is not None:
                try:
                    self._process_buttons()
                    self._process_hats()
                    self._process_axes()
                except Exception as exc:
                    print(f"warning: controller read failed: {exc}")
                    self._drop_joystick()
            time.sleep(max(poll_interval_ms, 1) / 1000.0)

    def _ensure_joystick(self, selected_index):
        controller_count = pygame.joystick.get_count()
        if controller_count == 0:
            if not self.warned_no_controller:
                print("warning: no controller detected; waiting for a controller")
                self.warned_no_controller = True
            self._drop_joystick()
            return
        self.warned_no_controller = False
        if selected_index >= controller_count:
            print(
                f"warning: selected_controller_index {selected_index} is not available; using controller 0 instead"
            )
            selected_index = 0
        if self.joystick is not None and self.joystick.get_init():
            return
        joystick = pygame.joystick.Joystick(selected_index)
        joystick.init()
        self.joystick = joystick
        self.joystick_instance_id = joystick.get_instance_id()
        self.button_state.clear()
        self.hat_state.clear()
        self.axis_state.clear()
        self.axis_raw_values.clear()
        self.warned_missing_buttons.clear()
        self.warned_missing_hats.clear()
        self.warned_missing_axes.clear()
        print(f"Using controller index {selected_index}: {joystick.get_name()}")
        if self.debug:
            print(f"detected controller name: {joystick.get_name()}")
            print(f"buttons: {joystick.get_numbuttons()} hats: {joystick.get_numhats()} axes: {joystick.get_numaxes()}")

    def _drop_joystick(self):
        if self.joystick is not None:
            self.sender.release_all()
            try:
                self.joystick.quit()
            except Exception:
                pass
        self.joystick = None
        self.joystick_instance_id = None
        self.button_state.clear()
        self.hat_state.clear()
        self.axis_state.clear()
        self.axis_raw_values.clear()
        self.warned_missing_buttons.clear()
        self.warned_missing_hats.clear()
        self.warned_missing_axes.clear()

    def _process_buttons(self):
        button_map = self.config.get("button_map", {})
        button_count = self.joystick.get_numbuttons()
        for button_name, key_name in button_map.items():
            button_index = int(button_name)
            if button_index >= button_count:
                if button_index not in self.warned_missing_buttons:
                    print(
                        f"warning: config button_map references button {button_index}, but controller only has {button_count} buttons"
                    )
                    self.warned_missing_buttons.add(button_index)
                self._apply_digital_mapping(key_name, False)
        for button_index in range(button_count):
            pressed = bool(self.joystick.get_button(button_index))
            previous = self.button_state.get(button_index, False)
            if pressed == previous:
                continue
            self.button_state[button_index] = pressed
            key_name = button_map.get(str(button_index))
            if self.debug:
                state_name = "pressed" if pressed else "released"
                if key_name:
                    print(f"button {button_index} {state_name} -> {key_name}")
                else:
                    print(f"button {button_index} {state_name} (unmapped)")
            if key_name:
                self._apply_digital_mapping(key_name, pressed)

    def _process_hats(self):
        hat_map = self.config.get("hat_map", {})
        hat_count = self.joystick.get_numhats()
        for hat_name, direction_map in hat_map.items():
            hat_index = int(hat_name)
            if hat_index >= hat_count:
                if hat_index not in self.warned_missing_hats:
                    print(
                        f"warning: config hat_map references hat {hat_index}, but controller reports {hat_count} hats"
                    )
                    self.warned_missing_hats.add(hat_index)
                for key_name in direction_map.values():
                    self._apply_digital_mapping(key_name, False)
        for hat_index in range(hat_count):
            current = self.joystick.get_hat(hat_index)
            previous = self.hat_state.get(hat_index, (0, 0))
            if current == previous:
                continue
            self.hat_state[hat_index] = current
            direction_map = hat_map.get(str(hat_index), {})
            if self.debug:
                if direction_map:
                    print(f"hat {hat_index} changed from {previous} to {current} -> {direction_map}")
                else:
                    print(f"hat {hat_index} changed from {previous} to {current} (unmapped)")
            states = {
                "left": current[0] < 0,
                "right": current[0] > 0,
                "up": current[1] > 0,
                "down": current[1] < 0,
            }
            for direction_name, key_name in direction_map.items():
                self._apply_digital_mapping(key_name, states.get(direction_name, False))

    def _process_axes(self):
        axis_map = self.config.get("axis_map", {})
        axis_count = self.joystick.get_numaxes()
        for axis_name, mapping in axis_map.items():
            axis_index = int(axis_name)
            if axis_index >= axis_count:
                if axis_index not in self.warned_missing_axes:
                    print(
                        f"warning: config axis_map references axis {axis_index}, but controller only has {axis_count} axes"
                    )
                    self.warned_missing_axes.add(axis_index)
                negative_key = mapping.get("negative")
                positive_key = mapping.get("positive")
                if negative_key:
                    self._apply_digital_mapping(negative_key, False)
                if positive_key:
                    self._apply_digital_mapping(positive_key, False)
        for axis_index in range(axis_count):
            mapping = axis_map.get(str(axis_index), {})
            raw_value = float(self.joystick.get_axis(axis_index))
            deadzone = self._get_axis_deadzone(mapping)
            value = self._apply_axis_deadzone(raw_value, deadzone)
            rounded = round(value, 3)
            previous_raw = self.axis_raw_values.get(axis_index)
            if self.debug and rounded != previous_raw:
                if mapping:
                    print(f"axis {axis_index} value {rounded} -> {mapping} deadzone={deadzone}")
                else:
                    print(f"axis {axis_index} value {rounded} (unmapped, deadzone={deadzone})")
            self.axis_raw_values[axis_index] = rounded
            threshold = float(mapping.get("threshold", 0.5))
            state = 0
            if value <= -threshold:
                state = -1
            elif value >= threshold:
                state = 1
            previous_state = self.axis_state.get(axis_index, 0)
            if state == previous_state:
                continue
            self.axis_state[axis_index] = state
            if self.debug:
                if mapping:
                    print(
                        f"axis {axis_index} direction changed from {previous_state} to {state} "
                        f"at threshold {threshold} with deadzone {deadzone}"
                    )
                else:
                    print(
                        f"axis {axis_index} direction changed from {previous_state} to {state} "
                        f"at threshold {threshold} with deadzone {deadzone} (unmapped)"
                    )
            negative_key = mapping.get("negative")
            positive_key = mapping.get("positive")
            if negative_key:
                self._apply_digital_mapping(negative_key, state == -1)
            if positive_key:
                self._apply_digital_mapping(positive_key, state == 1)

    def _apply_digital_mapping(self, key_name, active):
        if key_name is None:
            return
        try:
            if active:
                self.sender.press(key_name)
            else:
                self.sender.release(key_name)
        except KeyError as exc:
            print(f"warning: {exc}")
