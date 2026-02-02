"""View for RawRplModel."""

from builtins import property
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

from raw_rpl_dms_tools.raw_rpl_model import RawRplModel, PathOrNone
from raw_rpl_dms_tools.tk_utilities import Tooltip, LabelText, ModalLoadingDialog
from raw_rpl_dms_tools.metadata import TITLE
from raw_rpl_dms_tools.icon import set_window_icon
from raw_rpl_dms_tools.transform import ROTATIONS


class RawRplView(ttk.Frame):
    """ttk.Frame view on RawRplModel."""
    def __init__(self, *args, model: RawRplModel, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.model = model
        self.grid_columnconfigure(0, weight=1)

        self._pad = (5, 5)

        self.rotations = ROTATIONS
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

        file = self.open_file_dialog(
            initial_path,
            "Select RAW file",
            [("RAW Files", "*.raw")],
        )

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

        file = self.open_file_dialog(
            initial_path,
            "Select RPL file",
            [("RPL Files", "*.rpl")],
        )

        if file:
            self.set_rpl_filepath(Path(file))
            self.generate_preview_listener(None)

        return

    def open_file_dialog(
        self,
        initial_path: str = "",
        title: str = "Select file",
        filetypes: list[tuple[str, str]] | None = None,
        show_all: bool = True,
    ) -> str:
        """Trigger 'Open file' dialog with optional initial path."""
        if filetypes is None:
            filetypes = []
        if show_all:
            filetypes.append(("All Files", "*"))
        file = filedialog.askopenfilename(
            title=title,
            multiple=False,  # type: ignore
            initialdir=initial_path,
            filetypes=filetypes,
        )
        return file

    def draw_preview_button(self, row: int) -> None:
        """Draw the generate preview button."""
        frame = ttk.Frame(master=self)
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
        transform_frame = ttk.Frame(master=self)
        transform_frame.grid(
            sticky="ew",
            column=0, row=row,
            padx=self._pad, pady=0,
        )
        transform_frame.grid_rowconfigure(1, weight=1)
        transform_frame.grid_columnconfigure(0, weight=1)
        transform_row = -1

        transform_row += 1
        label = ttk.Label(master=transform_frame, text="Transform")
        label.grid(
            sticky="w",
            column=0, row=transform_row,
            padx=0, pady=(0, self._pad[1]),
        )

        transform_row += 1
        frame = ttk.LabelFrame(master=transform_frame, text="Rotate counterclockwise")
        frame.grid(
            sticky="ew",
            column=0, row=transform_row,
            padx=0,
            pady=(0, self._pad[1]),
        )
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        row = -1

        for key, value in self.rotations.items():
            row += 1
            radiobutton = ttk.Radiobutton(
                frame,
                text=key,
                variable=self.rotations_key,
                value=key,
                command=lambda k=self.rotations_key: [
                    setattr(
                        self.model,
                        "rotate_turns",
                        value["turns"],
                    ),
                ],
            )
            radiobutton.grid(sticky="w", column=0, row=row)
            Tooltip(
                radiobutton,
                text=f"Rotate {key}."
            )

        transform_row += 1
        frame = ttk.Frame(master=transform_frame,)
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
        checkbutton = ttk.Checkbutton(
            frame,
            text="Generate preview of transformed copy",
            variable=self.generate_transform_preview,
            onvalue=1,
            offvalue=0,
            command=lambda g=self.generate_transform_preview: [],
        )
        checkbutton.grid(
            sticky="w",
            row=row,
            column=0,
            columnspan=2,
            padx=0, pady=0,
        )
        Tooltip(
            checkbutton,
            text=(
                "Generate a preview image of the transformed RAW-RPL and save as "
                "<transformed_raw_filename>.preview.png."
            )
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
        Tooltip(
            button,
            text=(
                "Transform and save a copy of the RAW-RPL file pair as "
                "<filename>_<transform>.raw/rpl, and then (optionally) generate a "
                "preview image as <raw_filename>_<transform>.preview.png."
            )
        )

    def draw_select_buttons(self, row: int) -> None:
        """Draw the select RAW and select RPL buttons."""
        frame = ttk.Frame(master=self)
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
        text = path.name if path else ""
        self.generate_preview_label.set_text(text=text)
        return

    def generate_preview(self) -> PathOrNone:
        """Generate a preview with the model."""
        filepath = None

        dialog = set_window_icon(
            ModalLoadingDialog(master=self, text="Generating preview from RAW-RPL...")
        )
        dialog.update()  # Works, but I really should multi-thread with root.after()...
        try:
            filepath = self.model.generate_preview()
        except Exception as error:
            message = f"Error while generating preview:\n\n{str(error)}"
            messagebox.showerror(TITLE, message,)
            self.generate_preview_label.set_text("")
        else:
            message = f"Preview generated:\n\n{filepath}"
            messagebox.showinfo(TITLE, message,)
        finally:
            dialog.destroy()

        return filepath

    def transform_and_save_copy_listener(
        self,
        raw: PathOrNone,
        rpl: PathOrNone,
        preview: PathOrNone,
    ) -> None:
        """Listener for self.transform_and_save_copy."""
        text: str = ""
        if raw and rpl:
            text = f"{raw.name}, {''.join(rpl.suffixes)}"
            if preview:
                text += f", {''.join(preview.suffixes)}"

        self.transform_label.set_text(text)
        return

    def transform_and_save_copy(
        self,
        preview: bool = True,
    ) -> tuple[PathOrNone, PathOrNone, PathOrNone]:
        """Transform and save a RAW-RPL copy with an optional preview with the model."""
        raw_tr: PathOrNone = None
        rpl_tr: PathOrNone = None
        preview_tr: PathOrNone = None

        dialog = set_window_icon(
            ModalLoadingDialog(master=self, text="Transforming and saving RAW-RPL...")
        )
        dialog.update()
        try:
            raw_tr, rpl_tr = self.model.transform_and_save_copy()
        except Exception as error:
            message = f"Error while transforming and saving RAW-RPL:\n\n{str(error)}"
            messagebox.showerror(TITLE, message,)
            self.transform_and_save_copy_listener(raw_tr, rpl_tr, preview_tr)
            return raw_tr, rpl_tr, preview_tr
        else:
            message = f"Transformed RAW-RPL saved:\n\n{raw_tr}\n{rpl_tr}"
            messagebox.showinfo(TITLE, message,)
        finally:
            dialog.destroy()

        if preview:
            dialog = set_window_icon(
                ModalLoadingDialog(
                    master=self,
                    text="Generating preview of transformed RAW-RPL..."
                )
            )
            dialog.update()
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
                self.transform_and_save_copy_listener(raw_tr, rpl_tr, preview_tr)
                return raw_tr, rpl_tr, preview_tr
            else:
                message = f"Preview of transformed RAW-RPL generated:\n\n{preview_tr}"
                messagebox.showinfo(TITLE, message,)
            finally:
                dialog.destroy()

        self.transform_and_save_copy_listener(raw_tr, rpl_tr, preview_tr)

        return raw_tr, rpl_tr, preview_tr
