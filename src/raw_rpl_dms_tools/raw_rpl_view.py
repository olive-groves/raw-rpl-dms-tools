"""View for RawRplModel."""

from builtins import property
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

from raw_rpl_dms_tools.raw_rpl_model import RawRplModel, PathOrNone
from raw_rpl_dms_tools.tk_utilities import Tooltip, LabelText
from raw_rpl_dms_tools.metadata import TITLE


class RawRplView(tk.Frame):
    """tk.Frame view on RdzRplModel."""
    def __init__(self, *args, model: RawRplModel, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.model = model
        self.grid_columnconfigure(0, weight=1)

        self._pad = (5, 5)

        self.rotations = {
            "90° left (counterclockwise)": {
                "turns": 1,
            },
            "90° right (clockwise)": {
                "turns": 3,
            },
            "180°": {
                "turns": 2,
            },
        }
        default_turns = 1
        self.model.rotate_turns = default_turns
        rotations_key_str = next(
            (k for k, v in self.rotations.items() if v.get("turns") == default_turns),
        )
        self.rotations_key = tk.StringVar(master=self, value=f"{rotations_key_str}")

        row = -1

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

        self.grid_rowconfigure(row, weight=1)

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
            multiple=False,  # type: ignore
            initialdir=initial_path,
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
        label = LabelText(master=frame, text="", justify="right")
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
        """Draw the transform frame and rotate subframe."""
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
            padx=0, pady=(0, self._pad[1]),
        )

        transform_row += 1
        frame = tk.LabelFrame(master=transform_frame, text="Rotate")
        frame.grid(
            sticky="ew",
            column=0, row=transform_row,
            padx=0,
            pady=(0, self._pad[1]),
        )
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        row = -1

        for rotation in self.rotations.keys():
            row += 1
            tk.Radiobutton(
                frame,
                text=rotation,
                variable=self.rotations_key,
                value=rotation,
                command=lambda k=self.rotations_key: [
                    setattr(
                        self.model,
                        "rotate_turns",
                        self.rotations[k.get()]["turns"],
                    ),
                    print(k.get()),
                ],
            ).grid(sticky="w", column=0, row=row)

        transform_row += 1
        frame = tk.Frame(master=transform_frame,)
        frame.grid(
            sticky="ew",
            column=0, row=transform_row,
            padx=0, pady=0,
        )
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        row = -1

        row += 1
        self.generate_transform_preview = tk.IntVar(master=self, value=1)
        col = 0
        tk.Checkbutton(
            frame,
            text="Generate preview of transformed copy",
            variable=self.generate_transform_preview,
            onvalue=1,
            offvalue=0,
            command=lambda g=self.generate_transform_preview: [],
        ).grid(
            sticky="w",
            row=row,
            column=0,
            columnspan=2,
            padx=0, pady=0,
        )

        row += 1
        col = 0
        label = LabelText(master=frame, text="", justify="right")
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
            command=lambda p=self.generate_transform_preview: [
                self.transform_and_save_copy(preview=bool(p.get())),
            ]
        )
        button.grid(
            sticky="e",
            column=1, row=row,
            padx=0, pady=self._pad,
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
        label = LabelText(master=frame, text="No RAW file selected", justify="left")
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
        label = LabelText(master=frame, text="No RPL file selected", justify="left")
        label.grid(
            sticky="w",
            column=col, row=row,
            padx=0, pady=0,
        )
        self.rpl_label = label

        return

    def _set_path(self, property_: property, path: PathOrNone) -> None:
        """Call the setter of a model path property."""
        instance = self.model

        if property_.fset is None:
            raise AttributeError(f"Instance {instance} has no setter for {property_}.")

        try:
            property_.fset(instance, path)
        except Exception:
            property_.fset(instance, None)
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
            path=path,
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
            path=path,
        )

    def rotate_turns_listener(self, turns: int) -> None:
        """Listener for RawRplModel.rotate_turns."""
        return

    def generate_preview_listener(self, path: PathOrNone) -> None:
        """Listener for RawRplModel.generate_preview."""
        text = str(path or "")
        self.generate_preview_label.set_text(text=text)
        return

    def generate_preview(self) -> PathOrNone:
        """Generate a preview with the model."""
        filepath = None
        try:
            filepath = self.model.generate_preview()
        except Exception as error:
            message = f"Error while generating preview:\n\n{str(error)}"
            messagebox.showerror(TITLE, message,)
        else:
            message = f"Preview generated:\n\n{filepath}"
            messagebox.showinfo(TITLE, message,)
        return filepath

    def transform_and_save_copy(
        self,
        preview: bool = True,
    ) -> tuple[PathOrNone, PathOrNone, PathOrNone]:
        """Transform and save a RAW-RPL copy with an optional preview with the model."""
        raw_tr: PathOrNone = None
        rpl_tr: PathOrNone = None
        preview_tr: PathOrNone = None
        try:
            raw_tr, rpl_tr = self.model.transform_and_save_copy()
        except Exception as error:
            message = f"Error while transforming and saving RAW-RPL:\n\n{str(error)}"
            messagebox.showerror(TITLE, message,)
            return raw_tr, rpl_tr, preview_tr
        else:
            message = f"Transformed RAW-RPL saved:\n\n{raw_tr}\n{rpl_tr}"
            messagebox.showinfo(TITLE, message,)

        if preview:
            try:
                model = RawRplModel()
                model.raw_filepath = raw_tr
                model.rpl_filepath = rpl_tr
                preview_tr = model.generate_preview()
            except Exception as error:
                message = (
                    "Error while generating preview of transformed RAW-RPL:\n\n"
                    f"{str(error)}"
                )
                messagebox.showerror(TITLE, message,)
                return raw_tr, rpl_tr, preview_tr
            else:
                message = f"Preview of transformed RAW-RPL generated:\n\n{preview_tr}"
                messagebox.showinfo(TITLE, message,)

        return raw_tr, rpl_tr, preview_tr
