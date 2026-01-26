"""View."""

from builtins import property
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

from raw_rpl_tools.model import RawRplModel, PathOrNone
from raw_rpl_tools.tk_utilities import Tooltip
from raw_rpl_tools.metadata import TITLE, SUMMARY, VERSION, HOMEPAGE, LICENSE_FILE


class RawRplView(tk.Frame):
    """tk.Frame view on RdzRplControl."""
    def __init__(self, window: tk.Tk, model: RawRplModel) -> None:
        super().__init__(master=window)
        self.model = model

        rows = 2
        cols = 0

        window.grid_rowconfigure(rows, weight=1)
        window.grid_columnconfigure(cols, weight=1)
        self._window = window

        self.grid()
        self.grid_rowconfigure(rows, weight=1)
        self.grid_columnconfigure(cols, weight=1)

        self._pad = (5, 5)

        row = -1

        # Draw About box
        row += 1
        self.draw_header(row)

        # Draw Open buttons
        row += 1
        self.draw_select_buttons(row=row)

        row += 1
        separator = ttk.Separator(window, orient='horizontal')
        separator.grid(
            sticky="new",
            column=0, row=row,
            padx=self._pad, pady=self._pad,
        )

        # TODO:
        # "Save as rotated copy"

        # # Draw output field
        # row += 1
        # self.draw_output(row=row)

        # # Draw settings (include CSV's, include JPG's, overwrite)
        # row += 1
        # self.draw_settings(row=row, overwrite=overwrite)

        # # Draw Extract & Save button
        # row += 1
        # self.draw_extract_and_save_button(row=row)

    def select_raw_via_dialog(self) -> None:
        """Trigger an Open File dialog to select and set the RAW filepath."""
        if existing_path := self.model.raw_filepath:
            initial_path = str(existing_path)
        else:
            initial_path = ""

        file = self.open_file_dialog(initial_path, "Select RAW file")

        if file:
            self.set_raw_filepath(Path(file))

        return

    def open_file_dialog(
        self,
        initial_path: str = "",
        title: str = "Select file"
    ) -> str:
        """Trigger 'Open file' dialog with optional initial path."""
        file = filedialog.askopenfilename(
            title=title,
            multiple=False,
            initialdir=initial_path
        )
        return file

    def draw_select_buttons(self, row: int) -> None:
        """Draw the select RAW and select RPL buttons."""
        frame = tk.Frame(master=self._window)
        frame.grid(
            sticky="ew",
            column=0, row=row,
            padx=(0, 0), pady=(0, 0),
        )
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)

        row = -1

        # RAW file
        row += 1
        col = 0
        text = "Select RAW file..."
        button = ttk.Button(
            frame,
            text=text,
            command=self.select_raw_via_dialog,
        )
        button.grid(
            sticky="we",
            column=col, row=0,
            padx=self._pad, pady=0,
        )
        Tooltip(button, text="Select a RAW file belonging to an accompanying RPL file.")

        col = 1
        label = ttk.Label(frame, text="No RAW file selected")
        label.grid(
            sticky="w",
            column=col, row=row,
            padx=self._pad, pady=0,
        )
        self.raw_label = label

        # TODO: Auto-find RPL based on selected RAW? Only do if RPL not selected?
        row += 1
        col = 0
        text = "Select RPL file..."
        button = ttk.Button(
            frame,
            text=text,
            command=lambda: self.clicked_open_directory,
        )
        button.grid(
            sticky="we",
            column=col, row=row,
            padx=self._pad, pady=0,
        )
        Tooltip(
            button,
            text="Select a RPL file belonging to an accompanying RAW file.",
        )

        col = 1
        label = ttk.Label(frame, text="No RPL file selected")
        label.grid(
            sticky="w",
            column=col, row=row,
            padx=self._pad, pady=0,
        )
        return

    def draw_header(self, row: int) -> None:
        """Draw the header of the app with the title and the About button."""
        col = -1

        frame = tk.Frame(master=self._window)
        frame.grid(
            sticky="ew",
            column=0, row=row,
            padx=(0, 0), pady=(0, 0)
        )
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        col += 1
        label = ttk.Label(frame, text=TITLE)
        label.grid(
            sticky="",
            column=col, row=0,
            padx=self._pad, pady=self._pad
        )

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
        Tooltip(button, text=f"About {TITLE}...")

    def _set_path(
        self,
        property_: property,
        path: PathOrNone,
        # notify: QtCore.pyqtSignal | QtCore.pyqtBoundSignal | None = None,
        prefix: str = "File"
    ) -> None:
        """Call the setter of a model path property.

        # set_ (QtCore.pyqtSignal): Signal to emit set value of property
        """
        instance = self.model

        if property_.fset is None:
            raise AttributeError(f"Instance {instance} has no setter for {property_}.")

        try:
            property_.fset(instance, path)
        except ValueError as e:
            message = str(e)
            severity = "error"
            status = "waiting"
            property_.fset(instance, None)
        except FileNotFoundError:
            message = f"{prefix} does not exist"
            severity = "error"
            status = "waiting"
            property_.fset(instance, None)
        except Exception:
            message = "Unexpected error; could not set"
            severity = "error"
            status = "waiting"
            property_.fset(instance, None)
        else:
            message = f"{prefix} selected"
            severity = "info"
            status = "done" if path else "waiting"
        # if notify:
        #     notify.emit(Notification(
        #         text=message, severity=severity, status=status))
        return

    def raw_filepath_listener(self, path: Path) -> None:
        """Listener for raw_filepath."""
        self.raw_label.config(text=str(path))
        return

    def set_raw_filepath(self, path: PathOrNone) -> None:
        """Set the RAW filepath of the model."""
        self._set_path(
            property_=RawRplModel.raw_filepath,
            # notify=self.h5_file_notify,
            path=path,
            prefix="RAW file"
        )


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
