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
    window.title(TITLE)
    window.geometry('320x294')

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
    app = RawRplView(model=model)
    model.observers.append(app)

    # Layout
    app.grid(
        row=0,
        column=0,
        sticky="nsew",
    )
    tk.Label(
        master=window,
        text="<3",
    ).grid(
        pady=4,
        row=1,
        column=0,sticky="nsew",
    )
    window.grid_rowconfigure(1, weight=1)  # Push app to top of window
    window.grid_columnconfigure(0, weight=1)

    window.mainloop()


if __name__ == "__main__":
    main()
