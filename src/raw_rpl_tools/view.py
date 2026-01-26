"""View."""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from raw_rpl_tools.tk_utilities import Tooltip
from raw_rpl_tools.metadata import TITLE, SUMMARY, VERSION, HOMEPAGE, LICENSE_FILE


class RawRplView(tk.Frame):
    """tk.Frame view on RdzRplControl."""
    def __init__(self, window: tk.Tk, overwrite: bool = False) -> None:
        super().__init__(master=window)
        rows = 2
        cols = 0

        window.grid_rowconfigure(rows, weight=1)
        window.grid_columnconfigure(cols, weight=1)
        self._window = window

        self.grid()
        self.grid_rowconfigure(rows, weight=1)
        self.grid_columnconfigure(cols, weight=1)

        # self._pdz_file_paths = []
        # self._pdz_folders = []
        # self._csv_suffix = '.pdz'
        # self._image_suffix = '-'
        # self._image_record_name = 'Image Details'
        # self._extensions = ["csv", "jpeg"]

        # self.pdz_tools = []

        # self._default_output_text = "No files or folder selected"

        # self._save_csv = True
        # self._save_jpeg = True

        self._pad = (5, 5)

        row = -1

        # Draw Refresh and About box
        row += 1
        col = -1

        frame = tk.Frame(master=self._window)
        frame.grid(sticky="ew",
                   column=0, row=row,
                   padx=(0, 0), pady=(0, 0))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        col += 1
        label = ttk.Label(frame, text=SUMMARY)
        label.grid(sticky="",
                   column=col, row=0,
                   padx=self._pad, pady=self._pad)

        col += 1
        text = "?"
        button = ttk.Button(
            frame,
            text=text,
            command=lambda: show_about(self._window),
            width=len(text) + 2
        )
        button.grid(
            sticky="e",
            column=col, row=0,
            padx=self._pad, pady=self._pad
        )
        self._about_button = button
        Tooltip(button, text=f"About {TITLE}...")

        # # Draw Open buttons
        # row += 1
        # self.draw_open_buttons(row=row)

        # # Draw output field
        # row += 1
        # self.draw_output(row=row)

        # # Draw settings (include CSV's, include JPG's, overwrite)
        # row += 1
        # self.draw_settings(row=row, overwrite=overwrite)

        # # Draw Extract & Save button
        # row += 1
        # self.draw_extract_and_save_button(row=row)


def show_about(window: tk.Tk) -> None:
        """Show the about page."""
        title = window.title()
        info = (
            f"{TITLE}"
            "\n\n"
            f"{SUMMARY}"
            "\n\n"
            f"Version {VERSION}"
            "\n\n"
            f"{HOMEPAGE}"
            "\n\n"
            f"{LICENSE_FILE}"
        )
        messagebox.showinfo(title, info)
