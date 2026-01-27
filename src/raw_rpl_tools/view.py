"""View."""

from builtins import property
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

from raw_rpl_tools.model import RawRplModel, PathOrNone
from raw_rpl_tools.tk_utilities import Tooltip, LabelText
from raw_rpl_tools.metadata import TITLE, SUMMARY, VERSION, HOMEPAGE, LICENSE_FILE


class RawRplView(tk.Frame):
    """tk.Frame view on RdzRplControl."""
    def __init__(self, window: tk.Tk, model: RawRplModel) -> None:
        super().__init__(master=window)
        self.model = model

        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)
        self._window = window

        self.grid(
            sticky="new",
        )
        self.grid_columnconfigure(0, weight=1)

        self._pad = (5, 5)

        row = -1

        # Draw About box
        row += 1
        self.draw_header(row)

        # Draw Select buttons
        row += 1
        self.draw_select_buttons(row=row)

        # Draw Generate preview button
        row += 1
        self.draw_preview_button(row=row)

        # Draw Separator
        row += 1
        separator = ttk.Separator(self, orient='horizontal')
        separator.grid(
            sticky="ew",
            column=0, row=row,
            padx=self._pad, pady=self._pad,
        )

        # Draw Rotation
        row += 1
        self.draw_transform_buttons(row=row)

        row += 1
        label = tk.Label(self, text="·")
        label.grid(
            sticky="s",
            column=0, row=row,
        )
        self.grid_rowconfigure(row - 1, weight=1)

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
            self.generate_preview_listener(None)

        return

    def select_rpl_via_dialog(self) -> None:
        """Trigger an Open File dialog to select and set the RPL filepath."""
        if existing_path := self.model.rpl_filepath:
            initial_path = str(existing_path)
        else:
            initial_path = ""

        file = self.open_file_dialog(initial_path, "Select RPL file")

        if file:
            self.set_rpl_filepath(Path(file))
            self.generate_preview_listener(None)

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

    def draw_preview_button(self, row: int) -> None:
        """Draw the generate preview button."""
        frame = tk.Frame(master=self)
        frame.grid(
            sticky="ew",
            column=0, row=row,
            padx=self._pad, pady=0,
        )
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)

        row = -1

        row += 1
        col = 0
        label = LabelText(window=frame, text="", justify="right")
        label.grid(
            sticky="e",
            column=col, row=row,
            padx=0, pady=0,
        )
        self.generate_preview_label = label

        col = 1
        text = "Generate Preview Image"
        button = ttk.Button(
            frame,
            text=text,
            command=self.generate_preview,
        )
        button.grid(
            sticky="we",
            column=col, row=row,
            padx=(self._pad[0], 0), pady=0,
        )
        Tooltip(
            button,
            text=(
                "Create a PNG preview image from the RAW-RPL pair and save as "
                "<raw_filename>.preview.png."
            )
        )
        return

    def draw_transform_buttons(self, row: int) -> None:
        transform_frame = tk.Frame(master=self)
        transform_frame.grid(
            sticky="ew",
            column=0, row=row,
            padx=self._pad, pady=0,
        )
        transform_frame.grid_rowconfigure(1, weight=1)
        transform_frame.grid_columnconfigure(0, weight=1)
        transform_row = -1

        transform_row += 1
        label = tk.Label(master=transform_frame, text="Transform")
        label.grid(
            sticky="w",
            column=0, row=transform_row,
            padx=0, pady=0,
        )

        transform_row += 1
        frame = tk.LabelFrame(master=transform_frame, text="Rotate")
        frame.grid(
            sticky="ew",
            column=0, row=transform_row,
            padx=self._pad, pady=(0, self._pad[1]),
        )
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        row = -1

        rotations = {
            "90° left (CCW ↺)": {
                "n": 1,
            },
            "90° right (CW ↻)": {
                "n": 3,
            },
            "180°": {
                "n": 2,
            },
        }

        self.variable = tk.StringVar(frame, f"{next(iter(rotations))}")
        # variable.get()

        for rotation in rotations.keys():
            row += 1
            tk.Radiobutton(
                frame,
                text=rotation,
                variable=self.variable,
                value=rotation,
                command=lambda x=self.variable: print(x.get()),
            ).grid(sticky="w", column=0, row=row)

        transform_row += 1
        frame = tk.Frame(master=transform_frame,)
        frame.grid(
            sticky="ew",
            column=0, row=transform_row,
            padx=0, pady=0,
        )
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        row = -1

        row += 1
        col = 0
        label = LabelText(window=frame, text="", justify="right")
        label.grid(
            sticky="e",
            column=col, row=row,
            padx=0, pady=0,
        )
        self.transform_label = label

        col += 1
        text = "Transform & Save Copy"
        button = ttk.Button(
            frame,
            text=text,
            # command=self.generate_preview,
        )
        button.grid(
            sticky="e",
            column=1, row=row,
            padx=self._pad, pady=self._pad,
        )

    def draw_select_buttons(self, row: int) -> None:
        """Draw the select RAW and select RPL buttons."""
        frame = tk.Frame(master=self)
        frame.grid(
            sticky="ew",
            column=0, row=row,
            padx=self._pad, pady=self._pad,
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
            column=col, row=row,
            padx=(0, self._pad[0]), pady=0,
        )
        Tooltip(button, text="Select a RAW file belonging to an accompanying RPL file.")
        col = 1
        label = LabelText(window=frame, text="No RAW file selected", justify="left")
        label.grid(
            sticky="w",
            column=col, row=row,
            padx=0, pady=0,
        )
        self.raw_label = label

        # RPL file
        row += 1
        col = 0
        text = "Select RPL file..."
        button = ttk.Button(
            frame,
            text=text,
            command=self.select_rpl_via_dialog,
        )
        button.grid(
            sticky="we",
            column=col, row=row,
            padx=(0, self._pad[0]), pady=0,
        )
        Tooltip(
            button,
            text="Select a RPL file belonging to an accompanying RAW file.",
        )
        col = 1
        label = LabelText(window=frame, text="No RPL file selected", justify="left")
        label.grid(
            sticky="w",
            column=col, row=row,
            padx=0, pady=0,
        )
        self.rpl_label = label

        return

    def draw_header(self, row: int) -> None:
        """Draw the header of the app with the title and the About button."""
        col = -1

        frame = tk.Frame(master=self)
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
        text = str(path or "")
        self.raw_label.set_text(text=text)
        return

    def set_raw_filepath(self, path: PathOrNone) -> None:
        """Set the RAW filepath of the model."""
        self._set_path(
            property_=RawRplModel.raw_filepath,
            # notify=self.h5_file_notify,
            path=path,
            prefix="RAW file"
        )

    def rpl_filepath_listener(self, path: Path) -> None:
        """Listener for rpl_filepath."""
        text = str(path or "")
        self.rpl_label.set_text(text=text)
        return

    def set_rpl_filepath(self, path: PathOrNone) -> None:
        """Set the RPL filepath of the model."""
        self._set_path(
            property_=RawRplModel.rpl_filepath,
            # notify=self.h5_file_notify,
            path=path,
            prefix="RPL file"
        )

    def generate_preview_listener(self, path: PathOrNone) -> None:
        """Listener for generate_preview."""
        text = str(path or "")
        self.generate_preview_label.set_text(text=text)
        return

    def generate_preview(self) -> PathOrNone:
        """Generate a preview with the model."""
        # Check if RAW and RPL set!
        # No? Error time ;)

        # try:
        #     self.model.generate
        # except Exception as e:
        #     showerror()>
        # raise NotImplementedError()
        error = None
        filepath = None
        try:
            filepath = self.model.generate_preview()
        except FileExistsError as e:
            error = str(e)
        except Exception as e:
            error = f"Error while generating preview:\n\n{e}"
        finally:
            if error:
                messagebox.showerror(self._window.title(), error)
            elif filepath:
                messagebox.showinfo(
                    self._window.title(),
                    f"Preview generated:\n\n{filepath}",
                )
        return


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
