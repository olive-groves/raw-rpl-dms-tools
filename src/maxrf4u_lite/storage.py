"""Stripped-down functions from `maxrf4u` `storage.py`.

maxrf4u Copyright (c) 2026 Frank Ligterink with changes by Lars Maxfield
"""

import os
import platform
import subprocess
import re
from pathlib import Path
from typing import Literal
from decimal import Decimal

import numpy as np

import png

WriteMode = Literal['w', 'x']
"""'w' truncate first; 'x' failing if the file already exists."""


def open_system_default(image: Path) -> None:
    """Open a file with the system's default application for that file's extension.

    Args:
        image: Absolute path to the file.
    """
    # Determine platform
    system = platform.system()

    match system:
        case "Linux":
            subprocess.call(["xdg-open", image])
        case "Darwin":
            subprocess.call(["open", image])
        case "Windows":
            os.startfile(image)  # type: ignore (module only found on Windows)
        case _:
            raise NotImplementedError(f"System '{system}' not supported.")


def make_raw_preview(
    raw_filepath: Path,
    rpl_filepath: Path,
    output_dir: Path | None = None,
    show: bool = False,
    save: bool = True,
    verbose: bool = False,
    overwrite: bool = False,
) -> Path | None:
    """Create single-channel 8-bit PNG of raw file to preview scan orientation."""
    if output_dir is not None and not output_dir.exists():
        raise FileNotFoundError(f"Folder does not exist at {output_dir}.")

    # read data cube shape and dtype from .rpl file
    dtype, shape = parse_rpl_keys(read_rpl(rpl_filepath, verbose=verbose))

    # create numpy memory map
    raw_mm = np.memmap(raw_filepath, dtype=dtype, mode='r', shape=shape)

    # create max-spectrum
    raw_flat = raw_mm.reshape([-1, shape[2]])
    raw_max = np.max(raw_flat, axis=0)

    # locate highest peak
    max_peak_idx = np.argmax(raw_max)

    # integrate max peak slice
    max_peak_map = np.average(raw_mm[:, :, max_peak_idx - 10:max_peak_idx + 10], axis=2)
    raw_preview = 255 * max_peak_map // np.amax(max_peak_map)

    suffix: str = '.preview.png'

    if output_dir is None:
        # save in same folder
        preview_filepath = raw_filepath.with_suffix(suffix)
    else:
        # save in output folder
        name = raw_filepath.with_suffix(suffix).name
        preview_filepath = output_dir / name

    if not overwrite and preview_filepath.exists():
        raise FileExistsError(f"Preview image already exists:\n\n{preview_filepath}")

    if save:
        print(f'Saving: {preview_filepath}...')
        png.from_array(raw_preview.astype(np.uint8), mode='L;8').save(preview_filepath)

    if show:
        print(f'Showing file: {preview_filepath}')
        open_system_default(preview_filepath)

    return preview_filepath


def rot90_raw_rpl(
    raw_filepath: Path,
    rpl_filepath: Path,
    output_dir: Path | None = None,
    n: int = 1,
    mode: WriteMode = 'x'
) -> tuple[Path, Path]:
    """Rotate and save a RAW and RPL by n×90 degrees."""
    if output_dir is not None and not output_dir.exists():
        raise FileNotFoundError(f"Folder does not exist at {output_dir}.")

    if output_dir is None:
        output_dir = raw_filepath.parent

    angle = n * 90 % 360
    append = f"_rot{angle}"

    rot_raw_filepath: Path = (
        output_dir / (raw_filepath.stem + append + raw_filepath.suffix)
    )
    rot_rpl_filepath: Path = (
        output_dir / (rpl_filepath.stem + append + rpl_filepath.suffix)
    )
    if rot_raw_filepath.exists() and mode != 'w':
        raise FileExistsError(f'RAW file already exists: {rot_raw_filepath}.')
    if rot_rpl_filepath.exists() and mode != 'w':
        raise FileExistsError(f'RPL file already exists: {rot_raw_filepath}.')

    keys = read_rpl(rpl_filepath)
    dtype, shape = parse_rpl_keys(keys)
    raw_mm = np.memmap(raw_filepath, dtype=dtype, mode='r', shape=shape)

    # Rotate RPL
    if n % 2:  # Switch height and width if 90, 270, ...
        height = keys["height"]["value"]
        keys["height"]["value"] = keys["width"]["value"]
        keys["width"]["value"] = height
    write_rpl(keys, rot_rpl_filepath, mode)

    # Rotate RAW
    rot_raw_mm = np.rot90(raw_mm, k=n)
    rot_shape = rot_raw_mm.shape
    out = np.memmap(rot_raw_filepath, dtype=dtype, mode='w+', shape=rot_shape)

    # Go by chunk instead of all at once.
    # out[:] = rot_raw_mm[:]
    chunk_size = 1
    total_rows = rot_shape[0]
    for i in range(0, total_rows, chunk_size):
        sl = slice(i, min(i + chunk_size, total_rows))
        data_chunk = rot_raw_mm[sl]
        out[sl] = data_chunk
        out.flush()

    return rot_raw_filepath, rot_rpl_filepath


def parse_rpl_keys(keys: dict) -> tuple[str, tuple[int, int, int]]:
    """Parse the keys of an RPL in the return format of `read_rpl()` to dtype and shape.

    Returns:
        Tuple containing the dtype (str) and shape (tuple).
    """
    width = int(keys['width']['value'])
    height = int(keys['height']['value'])
    depth = int(keys['depth']['value'])
    nbytes = int(keys['data-length']['value'])

    dtype = f'uint{nbytes * 8}'
    shape = (height, width, depth)

    return dtype, shape


def read_rpl(filepath: Path, verbose: bool = False) -> dict:
    """Read a RPL as a dict of dicts of each lowercase key, preserving case and spaces.

    Includes the first line 'key value' as a key.

    All values kept str.

    Per https://pages.nist.gov/NeXLSpectrum.jl/methods/.

    ```
    {
        'key': {
            'key': 'keY',
            'spaces': '    ',
            'value': 'value',
        },
        'width': {  # lowercase
            'key': 'wIdtH',  # preserved case
            'spaces': '     ',  # preserved spaces
            'value': '849',
        },
        ...
    }
    ```
    """
    # read data cube shape from .rpl file
    with open(filepath, 'r') as fh:
        lines = fh.readlines()

    if verbose:
        print(f'Parsing {filepath}: ')
        for line in lines:
            print(line, end='\r')

    keys: dict = {}
    tab_space: str = '\t '
    for line in lines:
        [key_spaces, value_newline] = line.split(tab_space)
        [key, first_space, other_spaces] = key_spaces.partition(' ')
        [value, _] = value_newline.split('\n')
        keys[key.lower()] = {
            "key": key,
            "spaces": first_space + other_spaces,
            "value": value,
        }

    return keys


def write_rpl(rpl: dict, filepath: Path, mode: WriteMode = 'x') -> None:
    """Write a case-sensitive RPL from a dict of nested dicts by key (`read_rpl`)."""
    tab_space: str = '\t '
    newline: str = '\n'
    lines = [
        k["key"] + k["spaces"] + tab_space + k["value"] + newline for k in rpl.values()
    ]
    string = ''.join(lines)
    with open(filepath, mode) as f:
        f.write(string)

    return None


def parse_dms_header_dimensions(line: bytes) -> tuple[int, int, int]:
    """Parse the dimensions line of a DMS header with respect to the DMS shape.

    Dimensions are in the DMS shape and can be directly passed to np.memmap:
        (images <rows>, height <cols>, width <depth>)
    """
    dimensions_list: list[int] = [
        int(dimension) for dimension in line.decode('ascii').strip().split()
    ]
    dimensions: tuple[int, int, int] = (
        dimensions_list[2],  # depth -> images
        dimensions_list[1],  # height -> rows
        dimensions_list[0],  # width -> cols
    )
    return dimensions


def split_dms_header_dimensions(line: bytes) -> tuple[bytes, bytes, bytes]:
    """Split the dimensions line of a DMS header."""
    match = re.match(
        (
            rb"(\s*\d+)"
            rb"(\s+\d+)"
            rb"(\s+\d+.*)"
        ),
        line,
        re.DOTALL,  # Catch newline.
    )
    if not match:
        raise ValueError(
            "Line does not match "
            "'<whitespace><num><whitespace><num><whitespace><num><suffix>'"
        )
    return match.groups()  # type: ignore - Regex match logically must return three.


def read_dms_header(filepath: Path) -> tuple[bytes, bytes]:
    """Get the first two lines of a DMS as binary strings.

    Size of the header can be determined with:
    ```
    sum([len(line) for line in lines])
    ```
    """
    with open(filepath, 'rb') as file:
        lines: tuple[bytes, bytes] = (file.readline(), file.readline())
    return lines


def read_dms_elemental_names(
        filepath: Path,
        header_size: int,
        dimensions: tuple[int, int, int],
) -> tuple[list[bytes], list[str]]:
    """Get the names of the elemental distribution images of a DMS.

    Returns:
        Tuple containing the names as a list of binary strings and a list of decoded,
        stripped strings.
    """
    with open(filepath, 'rb') as file:
        offset: int = header_size + dimensions[1] * dimensions[0] * dimensions[2] * 4
        file.seek(offset)

        lines: list[bytes] = []
        names: list[str] = []
        while line := file.readline():
            lines.append(line)
            names.append(line.decode('utf-8').strip())

    return lines, names


def read_dms_images(
        filepath: Path,
        header_size: int,
        dimensions: tuple[int, int, int],
) -> np.typing.NDArray[np.float32]:
    """Read the images of a DMS as a memory map with shape (images, height, width)."""
    images: np.ndarray = np.memmap(
        filepath,
        mode='r',
        dtype=np.float32,
        offset=header_size,
        shape=dimensions,
    )
    return images


def save_dms_image(
    image: np.typing.NDArray[np.float32],
    path: Path,
    bitdepth: Literal[8, 16] = 16,
) -> None:
    """Save a single DMS image."""
    levels = 2 ** (bitdepth - 1)
    dtype: np.dtype = np.dtype(f"uint{bitdepth}")

    # Normalize to bit-depth
    minimum = image.min()
    maximum = image.max()
    image = levels * (image - minimum) / (maximum - minimum)
    image = image.astype(dtype)

    png.from_array(image, mode=f'L;{bitdepth}').save(path)
    return


Number = float | int | Decimal


def scientific(
    x: Number,
    precision: int = 2,
    width: int = 2,
) -> str:
    """Format a number in scientific notation with mantissa precision, exponent width.

    >> scientific(40.1234, 3, 3)

    "4.012E+001"

    Args:
        x: The value to format.
        precision: Precision of mantissa.
        width: Fixed width of the exponent in digits.

    Return:
        Formatted string.
    """
    e = "E"
    if isinstance(x, Decimal):
        sci = f"{x:.{precision}{e}}"
    else:
        sci = f"{float(x):.{precision}{e}}"

    mantissa, exp = sci.split(e)
    sign = exp[0]
    digits = exp[1:]

    exponent = f"{int(digits):0{width}d}"
    return f"{mantissa}{e}{sign}{exponent}"
