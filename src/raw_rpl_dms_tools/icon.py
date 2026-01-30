"""App icon functions."""

from os import path  # Path does not work with pyinstaller. You have been warned.
from platform import system

import tkinter as tk


def set_window_icon(window: tk.Toplevel | tk.Tk) -> tk.Toplevel | tk.Tk:
    """Set a window's icon."""
    platformD = system()
    icon = None

    if platformD == 'Darwin':
        icon = 'icon.icns'
    elif platformD == 'Windows':
        icon = 'icon.ico'
    if icon:
        try:
            icon_path = path.abspath(path.join(path.dirname(__file__), icon))
            window.iconbitmap(default=str(icon_path))
        except Exception as e:
            print(f"Unexpected error while setting icon: {e}. Continuing without icon.")

    return window
