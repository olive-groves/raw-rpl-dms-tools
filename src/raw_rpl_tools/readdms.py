"""Read a DMS using information from its corresponding RPL"""

from pathlib import Path
from typing import Literal

import numpy as np
import png

from maxrf4u_lite.storage import (
    read_dms_images,
    read_dms_header,
    read_dms_elemental_names,
    open_system_default,
)

# rpl_filepath = Path(r"C:\art\data-NOBACKUP\xrf\spectral-datacube.rpl")
dms_filepath = Path(r"C:\art\data-NOBACKUP\xrf\elemental-datacube.dms")

header_lines, dimensions = read_dms_header(dms_filepath)
header_size = sum([len(line) for line in header_lines])
names_lines, names = read_dms_elemental_names(dms_filepath, header_size, dimensions)
images = read_dms_images(dms_filepath, header_size, dimensions)

for i, name in zip(range(images.shape[0]), names):
    bitdepth: Literal[8, 16] = 16
    dtype: np.dtype = np.dtype(f"uint{bitdepth}")
    levels = 2 ** (bitdepth - 1)
    image_memmap = images[i, :, :]
    minimum = image_memmap.min()
    maximum = image_memmap.max()
    image = levels * (image_memmap - minimum) / (maximum - minimum)
    image = image.astype(dtype)
    image_filepath = dms_filepath.with_suffix(f".{i}.preview.png")
    png.from_array(image, mode=f'L;{bitdepth}').save(image_filepath)

# open_system_default(image_filepath)

# get np array (memmap?)
# rotate it
# pass to write_dms? as a simple memmap? can you do that bruh

# write dms
# write_dms(filepath, header_lines, images, names_lines)

print("end")
