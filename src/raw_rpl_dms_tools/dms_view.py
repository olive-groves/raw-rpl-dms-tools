"""View for DmsModel."""

from builtins import property
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

from raw_rpl_dms_tools.dms_model import DmsModel, PathOrNone
from raw_rpl_dms_tools.tk_utilities import Tooltip, LabelText, ModalLoadingDialog
from raw_rpl_dms_tools.metadata import TITLE
from raw_rpl_dms_tools.icon import set_window_icon


def s(n: int) -> str:
    """Return 's' if multiple or zero, else ''."""
    return "" if n == 1 else "s"


class DmsView(ttk.Frame):
    """ttk.Frame view on DmsModel."""
    def __init__(self, *args, model: DmsModel, **kwargs) -> None:
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

        # Draw Select button
        row += 1
        self.draw_select(row=row)

        # Draw Extract elemental distribution images button
        row += 1
        self.draw_extract(row=row)

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
        self.draw_transform(row=row)

        self.grid_rowconfigure(row, weight=1)

    def select_dms_via_dialog(self) -> None:
        """Trigger an Open File dialog to select and set the DMS filepath."""
        if existing_path := self.model.dms_filepath:
            initial_path = str(existing_path)
        else:
            initial_path = ""

        file = self.open_file_dialog(
            initial_path,
            "Select DMS file",
            [("DMS Files", "*.dms")]
        )

        if file:
            self.set_dms_filepath(Path(file))
            self.extract_listener(names=[], paths=[])

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

    def draw_extract(self, row: int) -> None:
        """Draw the extract elemental distribution images widgets."""
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
        self.extract_label = label

        col = 1
        text = "Extract Images"
        button = ttk.Button(
            frame,
            text=text,
            command=self.extract,
        )
        button.grid(
            sticky="we",
            column=col, row=row,
            padx=(self._pad[0], 0), pady=0,
        )
        Tooltip(
            button,
            text=(
                "Extract the elemental distribution images from the DMS and save each "
                "as <dms_filename>_<elemental name>.png."
            )
        )
        return

    def draw_transform(self, row: int) -> None:
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
        frame = ttk.LabelFrame(master=transform_frame, text="Rotate")
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
            ttk.Radiobutton(
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
                ],
            ).grid(sticky="w", column=0, row=row)

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
        self.extract_transform_preview = tk.IntVar(master=self, value=1)
        col = 0
        checkbutton = ttk.Checkbutton(
            frame,
            text="Extract images from transformed copy",
            variable=self.extract_transform_preview,
            onvalue=1,
            offvalue=0,
            command=lambda g=self.extract_transform_preview: [],
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
                "Extract the elemental distribution images from the transformed DMS and"
                "save each as <transformed_dms_filename>_<elemental name>.png."
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
            command=lambda p=self.extract_transform_preview: [
                self.transform_and_save_copy(extract=bool(p.get())),
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
                "Transform and save a copy of the DMS file as "
                "<dms_filename>_<transform>.dms, and then (optionally) extract each of "
                "its elemental distribution images as "
                "<dms_filename>_<transform>_<elemental name>.png."
            )
        )

    def draw_select(self, row: int) -> None:
        """Draw the select DMS button."""
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

        # DMS file
        row += 1
        col = 0
        text = "Select DMS file..."
        button = ttk.Button(
            frame,
            text=text,
            command=self.select_dms_via_dialog,
        )
        button.grid(
            sticky="we",
            column=col, row=row,
            padx=(0, self._pad[0]), pady=0,
        )
        Tooltip(button, text="Select a DMS file from Datamuncher.")
        col = 1
        label = LabelText(master=frame, text="No DMS file selected", justify="left")
        label.grid(
            sticky="w",
            column=col, row=row,
            padx=0, pady=0,
        )
        self.dms_label = label

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

    def dms_filepath_listener(self, path: Path) -> None:
        """Listener for dms_filepath."""
        text = str(path or "")
        self.dms_label.set_text(text=text)
        return

    def set_dms_filepath(self, path: PathOrNone) -> None:
        """Set the DMS filepath of the model."""
        self._set_path(
            property_=DmsModel.dms_filepath,
            path=path,
        )

    def rotate_turns_listener(self, turns: int) -> None:
        """Listener for DmsModel.rotate_turns."""
        return

    def extract_listener(self, names: list[str], paths: list[Path]) -> None:
        """Listener for DmsModel.extract."""
        if names:
            n = len(names)
            text = f"({n}) " + ", ".join(names)
        else:
            text = ""
        self.extract_label.set_text(text=text)
        return

    def extract(self) ->  tuple[list[str], list[Path]]:
        """Extract the elemental distribution images with the model."""
        names = []
        paths = []

        dialog = set_window_icon(
            ModalLoadingDialog(master=self, text="Extracting from DMS...")
        )
        dialog.update()  # Works, but I really should multi-thread with root.after()...
        try:
            names, paths = self.model.extract()
        except Exception as error:
            message = f"Error while generating preview:\n\n{str(error)}"
            messagebox.showerror(TITLE, message,)
            self.extract_label.set_text("")
        else:
            n = len(names)
            message = (
                f"{n} elemental distribution image{s(n)} extracted:\n\n"
                f"{'\n'.join(str(path) for path in paths)}"
            )
            messagebox.showinfo(TITLE, message,)
        finally:
            dialog.destroy()

        return names, paths

    def transform_and_save_copy(
        self,
        extract: bool = True,
    ) -> tuple[PathOrNone, list[Path]]:
        """Transform and save a DMS copy with an optional extraction."""
        dms_tr: PathOrNone = None
        extract_tr: list[Path] = []

        dialog = set_window_icon(
            ModalLoadingDialog(master=self, text="Transforming and saving DMS...")
        )
        dialog.update()
        try:
            dms_tr = self.model.transform_and_save_copy()
        except Exception as error:
            message = f"Error while transforming and saving DMS:\n\n{str(error)}"
            messagebox.showerror(TITLE, message,)
            self.transform_and_save_copy_listener(dms_tr, extract_tr)
            return dms_tr, extract_tr
        else:
            message = f"Transformed DMS saved:\n\n{dms_tr}"
            messagebox.showinfo(TITLE, message,)
        finally:
            dialog.destroy()

        if extract:
            dialog = set_window_icon(
                ModalLoadingDialog(
                    master=self,
                    text="Extracting from transformed DMS..."
                )
            )
            dialog.update()
            try:
                model = DmsModel()
                model.dms_filepath = dms_tr
                _, extract_tr = model.extract()
            except Exception as error:
                message = (
                    "Error while extracting images from transformed DMS:\n\n"
                    f"{str(error)}"
                )
                messagebox.showerror(TITLE, message,)
                self.transform_and_save_copy_listener(dms_tr, extract_tr)
                return dms_tr, extract_tr
            else:
                message = (
                    "Images from transformed DMS extracted:\n\n"
                    f"{'\n'.join(str(path) for path in extract_tr)}"
                )
                messagebox.showinfo(TITLE, message,)
            finally:
                dialog.destroy()

        self.transform_and_save_copy_listener(dms_tr, extract_tr)
        return dms_tr, extract_tr

    def transform_and_save_copy_listener(
        self,
        dms: PathOrNone,
        extract: list[Path],
    ) -> None:
        """Listener for self.transform_and_save_copy."""
        text: str = ""
        if dms:
            text = f"{dms.name}"
            if extract:
                text += f", ({len(extract)}) {''.join(extract[0].suffixes)}"

        self.transform_label.set_text(text)
        return
