"""Run RAW RPL Tools."""


from os import path
# from pathlib import Path
from platform import system
import tkinter as tk

from raw_rpl_dms_tools.metadata import TITLE
from raw_rpl_dms_tools.app import App


def main() -> None:
    """Main window."""
    window = tk.Tk()
    window.title(TITLE)
    window.geometry('320x400')
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)

    App(master=window).grid(row=0, column=0, sticky="nsew")

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

    window.mainloop()


if __name__ == "__main__":
    main()
