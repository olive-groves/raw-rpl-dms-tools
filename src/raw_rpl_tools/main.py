"""Run RAW RPL Tools."""


from os import path
from platform import system
import tkinter as tk

from raw_rpl_tools.metadata import TITLE
from raw_rpl_tools.model import RawRplModel
from raw_rpl_tools.view import RawRplView


def main() -> None:
    """Main window."""
    window = tk.Tk()
    window.title(f"{TITLE}")
    window.geometry('780x600')

    # Set icon based on operating system
    platformD = system()
    icon = None
    if platformD == 'Darwin':
        icon = 'icon.icns'
    elif platformD == 'Windows':
        icon = 'icon.ico'
    if icon:
        try:
            icon_path = path.abspath(path.join(path.dirname(__file__), icon))
            window.iconbitmap(icon_path)
        except Exception as e:
            print(f"Unexpected error while setting icon: {e}. Continuing without icon.")
            pass

    model = RawRplModel()
    app = RawRplView(window=window, model=model)
    model.observers.append(app)
    app.mainloop()


if __name__ == "__main__":
    main()
