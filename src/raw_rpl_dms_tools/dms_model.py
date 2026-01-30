"""Model for DMS functions."""

from pathlib import Path

import numpy as np

from raw_rpl_dms_tools.signaler import Signaler
from maxrf4u_lite.storage import (
    read_dms_images,
    read_dms_header,
    parse_dms_header_dimensions,
    read_dms_elemental_names,
    split_dms_header_dimensions,
    save_dms_image,
)

PathOrNone = Path | None


class DmsModel(Signaler):
    """maxrf4u_lite DMS functions bundled as a model."""
    def __init__(self) -> None:
        super().__init__()
        self.observers = []
        self.initialize()

    def initialize(self) -> None:
        """Initialize model."""
        self.dms_filepath = None
        self.rotate_turns = 0
        self.overwrite = False
        return

    @property
    def dms_filepath(self) -> PathOrNone:
        """File path to DMS file."""
        return self._dms_filepath

    @dms_filepath.setter
    def dms_filepath(self, path: PathOrNone) -> None:
        if path and not path.is_file():
            raise FileNotFoundError("File does not exist.")
        self._dms_filepath = path
        self._signal(path)

    @property
    def rotate_turns(self) -> int:
        """Amount of 90-degree turns to rotate."""
        return self._rotate_turns

    @rotate_turns.setter
    def rotate_turns(self, turns: int) -> None:
        self._rotate_turns = turns
        self._signal(turns)

    @property
    def overwrite(self) -> bool:
        """Whether to overwrite existing files."""
        return self._overwrite

    @overwrite.setter
    def overwrite(self, overwrite: bool) -> None:
        self._overwrite = overwrite
        self._signal(overwrite)

    def extract(self) -> tuple[list[str], list[Path]]:
        """Extract the elemental distribution images from the DMS."""
        if not (dms_filepath := self.dms_filepath):
            raise Exception("DMS file not defined.")

        header_lines = read_dms_header(dms_filepath)
        header_size = sum([len(line) for line in header_lines])
        dimensions_line = header_lines[1]
        dimensions = parse_dms_header_dimensions(dimensions_line)
        _, names = read_dms_elemental_names(dms_filepath, header_size, dimensions)

        # "All or nothing": Check if all available. If not, raise which ones.
        paths = [
            dms_filepath.parent / f"{dms_filepath.stem}_{''.join(name.split())}.png"
            for name in names
        ]
        existing: list[Path] = [path for path in paths if path.is_file()]
        if existing:
            raise FileExistsError(
                "No extracted images saved. One or more already exist:\n\n"
                f"{'\n'.join(str(path) for path in existing)}"
            )

        images = read_dms_images(dms_filepath, header_size, dimensions)
        for i, path in zip(range(images.shape[0]), paths):
            save_dms_image(images[i, :, :], path, 16)

        self._signal(names=names, paths=paths)

        return names, paths

    def transform_and_save_copy(self) -> PathOrNone:
        """Transform and save a copy of the DMS."""
        if not (dms_filepath := self.dms_filepath):
            raise Exception("DMS file not defined.")
        n = self.rotate_turns

        header_lines = read_dms_header(dms_filepath)
        header_size = sum([len(line) for line in header_lines])
        dimensions_line = header_lines[1]
        dimensions = parse_dms_header_dimensions(dimensions_line)
        names_lines, _ = read_dms_elemental_names(dms_filepath, header_size, dimensions)
        images = read_dms_images(dms_filepath, header_size, dimensions)

        # Rotate
        angle: int = n * 90 % 360
        dimensions_split = split_dms_header_dimensions(dimensions_line)
        images_rot = np.rot90(images, k=n, axes=(1, 2))
        if n % 2:
            dimensions_rot_split = (
                dimensions_split[1],
                dimensions_split[0],
                dimensions_split[2]
            )
        else:
            dimensions_rot_split = dimensions_split
        dimensions_rot_line: bytes = b"".join(dimensions_rot_split)
        header_rot_lines: list[bytes] = [
            header_lines[0],
            dimensions_rot_line
        ]

        # Write
        dms_tr_filepath = (
            dms_filepath.parent /
            (dms_filepath.stem + f"_rot{angle}" + dms_filepath.suffix)
        )
        if dms_tr_filepath.exists() and not self.overwrite:
            raise FileExistsError(f'DMS file already exists: {dms_tr_filepath}.')

        offset = 0

        # Write header
        with open(dms_tr_filepath, 'wb') as file:
            file.writelines(header_rot_lines)
        offset += sum([len(line) for line in header_rot_lines])

        # Write images
        out = np.memmap(
            dms_tr_filepath,
            dtype=np.float32,
            mode='r+',  # "w+" with offset does not work! You have been warned.
            shape=images_rot.shape,
            offset=offset,
        )
        out[:] = images_rot[:]
        # Go by chunk instead of all at once.
        # chunk_size = 1
        # total_rows = images_rot.shape[0]
        # for i in range(0, total_rows, chunk_size):
        #     sl = slice(i, min(i + chunk_size, total_rows))
        #     data_chunk = images_rot[sl]
        #     out[sl] = data_chunk
        #     out.flush()
        # offset += dimensions[0] * dimensions[1] * dimensions[2] * 4

        # Write elemental names
        with open(dms_tr_filepath, 'ab') as file:
            # file.seek(offset)
            file.writelines(names_lines)

        return dms_tr_filepath
