"""Application frame and supporting widgets for the main window."""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from raw_rpl_dms_tools.raw_rpl_model import RawRplModel
from raw_rpl_dms_tools.raw_rpl_view import RawRplView
from raw_rpl_dms_tools.dms_model import DmsModel
from raw_rpl_dms_tools.dms_view import DmsView
from raw_rpl_dms_tools.metadata import TITLE, SUMMARY, VERSION, HOMEPAGE, LICENSE_FILE
from raw_rpl_dms_tools.tk_utilities import Tooltip


class App(ttk.Frame):
    """Application frame with header and footer."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._pad = (5, 5)

        raw_rpl_model = RawRplModel()
        raw_rpl_view = RawRplView(master=self, model=raw_rpl_model)
        raw_rpl_model.observers.append(raw_rpl_view)

        dms_model = DmsModel()
        dms_view = DmsView(master=self, model=dms_model)
        dms_model.observers.append(dms_view)

        self.tabs = {
            "RAW-RPL": {
                "widget": raw_rpl_view,
            },
            "DMS": {
                "widget": dms_view,
            },
        }
        self.tab = tk.StringVar(self, f"{next(iter(self.tabs))}")

        # Layout
        row = -1
        col = 0

        row += 1
        self.draw_header(row)

        row += 1
        raw_rpl_view.grid(
            row=row,
            column=col,
            sticky="nsew",
        )
        dms_view.grid(
            row=row,
            column=col,
            sticky="nsew",
        )
        self.set_tab(self.tab.get())

        self.grid_rowconfigure(row + 1, weight=1)  # Everything to the top
        self.grid_columnconfigure(col, weight=1)

    def draw_header(self, row: int) -> None:
        """Draw the header of the app with the title and the About button."""
        col = -1

        frame = ttk.Frame(master=self)
        frame.grid(
            sticky="ew",
            column=0, row=row,
            padx=(0, 0), pady=(0, 0)
        )
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        col += 1
        tabbar = ttk.Frame(master=frame)
        tabbar.grid(
            sticky="ns",
            row=0,
            column=col,
            columnspan=2,
            padx=self._pad, pady=self._pad
        )
        tabbar.grid_rowconfigure(0, weight=1)
        tabbar.grid_columnconfigure(0, weight=1)

        tab_col = -1
        for i, tab in enumerate(self.tabs.keys()):
            tab_col += 1
            ttk.Radiobutton(
                tabbar,
                text=tab,
                variable=self.tab,
                value=tab,
                command=lambda x=self.tab: self.set_tab(x.get()),
            ).grid(row=0, column=i)

        col += 1
        text = "?"
        button = ttk.Button(
            frame,
            text=text,
            command=show_about,
            width=len(text) + 2
        )
        button.grid(
            sticky="e",
            column=col, row=0,
            padx=self._pad, pady=self._pad
        )
        Tooltip(button, text=f"About {TITLE}...")

    def set_tab(self, tab: str) -> None:
        """Set the activate tab using its key from self.tabs."""
        for key, value in self.tabs.items():
            widget: ttk.Frame | None = value.get("widget", None)
            if not widget:
                raise ValueError(f"Tab widget not specified for self.tabs['{key}'].")
            if key == tab:
                widget.grid()
            else:
                widget.grid_remove()
        return


def show_about() -> None:
        """Show the about page.

        FIXME: Move function and button to main/window level?
        """
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
        messagebox.showinfo(TITLE, info)
