"""
Hotkey parsing and key normalization for pynput.
"""

from pynput.keyboard import Key


def parse_hotkey(hotkey_str: str) -> set:
    """
    Parse a hotkey string like 'ctrl+shift+space' into a set of pynput Key objects.

    Supports: ctrl, shift, alt, cmd/win/super, space, enter, tab, esc,
    single characters, and any pynput Key attribute (f1-f12, etc.)
    """
    parts = [p.strip().lower() for p in hotkey_str.split("+")]
    keys = set()
    for p in parts:
        if p in {"ctrl", "control"}:
            keys.add(Key.ctrl)
        elif p in {"cmd", "cmd_l", "cmd_r", "win", "super"}:
            keys.add(Key.cmd)
        elif p in {"alt", "alt_l", "alt_gr"}:
            keys.add(Key.alt)
        elif p == "shift":
            keys.add(Key.shift)
        elif p == "space":
            keys.add(Key.space)
        elif p == "enter":
            keys.add(Key.enter)
        elif p == "tab":
            keys.add(Key.tab)
        elif p == "esc":
            keys.add(Key.esc)
        elif len(p) == 1:
            keys.add(p)
        else:
            try:
                keys.add(getattr(Key, p))
            except AttributeError:
                keys.add(p)
    return keys


def normalize_key(key) -> object:
    """
    Normalize left/right key variants to their generic form.
    e.g., Key.ctrl_l -> Key.ctrl, Key.shift_r -> Key.shift
    """
    try:
        name = key.name if hasattr(key, 'name') else str(key)
    except Exception:
        return key
    if name in ('ctrl_l', 'ctrl_r'):
        return Key.ctrl
    elif name in ('shift_l', 'shift_r'):
        return Key.shift
    elif name in ('alt_l', 'alt_r', 'alt_gr'):
        return Key.alt
    elif name in ('cmd_l', 'cmd_r'):
        return Key.cmd
    return key
