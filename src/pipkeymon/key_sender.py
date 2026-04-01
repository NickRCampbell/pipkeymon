import ctypes
from ctypes import wintypes


INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
ULONG_PTR = wintypes.WPARAM


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUTUNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", INPUTUNION),
    ]


SCAN_CODE_MAP = {
    "A": (0x1E, False),
    "B": (0x30, False),
    "C": (0x2E, False),
    "D": (0x20, False),
    "E": (0x12, False),
    "F": (0x21, False),
    "G": (0x22, False),
    "H": (0x23, False),
    "I": (0x17, False),
    "J": (0x24, False),
    "K": (0x25, False),
    "L": (0x26, False),
    "M": (0x32, False),
    "N": (0x31, False),
    "O": (0x18, False),
    "P": (0x19, False),
    "Q": (0x10, False),
    "R": (0x13, False),
    "S": (0x1F, False),
    "T": (0x14, False),
    "U": (0x16, False),
    "V": (0x2F, False),
    "W": (0x11, False),
    "X": (0x2D, False),
    "Y": (0x15, False),
    "Z": (0x2C, False),
    "0": (0x0B, False),
    "1": (0x02, False),
    "2": (0x03, False),
    "3": (0x04, False),
    "4": (0x05, False),
    "5": (0x06, False),
    "6": (0x07, False),
    "7": (0x08, False),
    "8": (0x09, False),
    "9": (0x0A, False),
    "SPACE": (0x39, False),
    "ESC": (0x01, False),
    "ESCAPE": (0x01, False),
    "ENTER": (0x1C, False),
    "TAB": (0x0F, False),
    "BACKSPACE": (0x0E, False),
    "UP": (0x48, True),
    "DOWN": (0x50, True),
    "LEFT": (0x4B, True),
    "RIGHT": (0x4D, True),
    "LSHIFT": (0x2A, False),
    "RSHIFT": (0x36, False),
    "LCTRL": (0x1D, False),
    "RCTRL": (0x1D, True),
    "LALT": (0x38, False),
    "RALT": (0x38, True),
}


def normalize_key_name(key_name):
    return str(key_name).strip().upper()


def key_name_to_scan_code(key_name):
    normalized = normalize_key_name(key_name)
    if normalized not in SCAN_CODE_MAP:
        raise KeyError(f"Unsupported key name: {key_name}")
    return SCAN_CODE_MAP[normalized]


class KeySender:
    def __init__(self, debug=False):
        self.debug = debug
        self.held_keys = set()
        self._user32 = ctypes.WinDLL("user32", use_last_error=True)
        self._send_input = self._user32.SendInput
        self._send_input.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
        self._send_input.restype = wintypes.UINT

    def press(self, key_name):
        scan_code, is_extended = key_name_to_scan_code(key_name)
        key_id = (scan_code, is_extended)
        if key_id in self.held_keys:
            return False
        self._send(scan_code, is_extended, key_up=False)
        self.held_keys.add(key_id)
        if self.debug:
            print(f"mapped action: key down {normalize_key_name(key_name)}")
        return True

    def release(self, key_name):
        scan_code, is_extended = key_name_to_scan_code(key_name)
        key_id = (scan_code, is_extended)
        if key_id not in self.held_keys:
            return False
        self._send(scan_code, is_extended, key_up=True)
        self.held_keys.discard(key_id)
        if self.debug:
            print(f"mapped action: key up {normalize_key_name(key_name)}")
        return True

    def release_all(self):
        for scan_code, is_extended in list(self.held_keys):
            self._send(scan_code, is_extended, key_up=True)
        self.held_keys.clear()
        if self.debug:
            print("mapped action: released all held keys")

    def _send(self, scan_code, is_extended, key_up):
        flags = KEYEVENTF_SCANCODE
        if is_extended:
            flags |= KEYEVENTF_EXTENDEDKEY
        if key_up:
            flags |= KEYEVENTF_KEYUP
        input_record = INPUT(
            type=INPUT_KEYBOARD,
            ki=KEYBDINPUT(
                wVk=0,
                wScan=scan_code,
                dwFlags=flags,
                time=0,
                dwExtraInfo=0,
            ),
        )
        sent = self._send_input(1, ctypes.byref(input_record), ctypes.sizeof(INPUT))
        if sent != 1:
            error_code = ctypes.get_last_error()
            raise OSError(f"SendInput failed with error {error_code}")
