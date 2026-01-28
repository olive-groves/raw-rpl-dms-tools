"""Read a DMS using information from its corresponding RPL"""

from pathlib import Path
from decimal import Decimal
from typing import Literal

import numpy as np
import png

from maxrf4u_lite.storage import (
    read_dms_images,
    read_dms_header,
    read_dms_elemental_names,
    save_dms_images,
    open_system_default,
)

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


dms_filepath = Path(r"C:\art\data-NOBACKUP\xrf\elemental-datacube.dms")

header_lines, dimensions = read_dms_header(dms_filepath)
header_size = sum([len(line) for line in header_lines])
names_lines, names = read_dms_elemental_names(dms_filepath, header_size, dimensions)
images = read_dms_images(dms_filepath, header_size, dimensions)

image_paths = [
    dms_filepath.parent / f"{dms_filepath.stem}_{''.join(name.split())}.png"
    for name in names
]
save_dms_images(images, image_paths, 16)

# get np array (memmap?)
# rotate it
# pass to write_dms? as a simple memmap? can you do that bruh

# write dms
# write_dms(filepath, header_lines, images, names_lines)

print("end")
