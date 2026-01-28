"""Read a DMS using information from its corresponding RPL"""

from pathlib import Path

import numpy as np

from maxrf4u_lite.storage import (
    read_dms_images,
    read_dms_header,
    parse_dms_header_dimensions,
    read_dms_elemental_names,
    split_dms_header_dimensions,
    save_dms_image,
)

dms_filepath = Path(r"C:\art\data-NOBACKUP\xrf\elemental-datacube.dms")

header_lines = read_dms_header(dms_filepath)
header_size = sum([len(line) for line in header_lines])
dimensions_line = header_lines[1]
dimensions = parse_dms_header_dimensions(dimensions_line)
names_lines, names = read_dms_elemental_names(dms_filepath, header_size, dimensions)
images = read_dms_images(dms_filepath, header_size, dimensions)


# Save images
image_paths = [
    dms_filepath.parent / f"{dms_filepath.stem}_{''.join(name.split())}.png"
    for name in names
]
for i, path in zip(range(images.shape[0]), image_paths):
    save_dms_image(images[i, :, :], path, 16)


# Rotate DMS
n: int = 3
angle = n * 90 % 360
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


# Write rotated DMS

# TODO: write_dms(filepath, header_lines, images, names_lines)
dms_rot_filepath = (
    dms_filepath.parent / (dms_filepath.stem + f"_rot{angle}" + dms_filepath.suffix)
)
overwrite = True
if dms_rot_filepath.exists() and not overwrite:
    raise FileExistsError(f'DMS file already exists: {dms_rot_filepath}.')

offset = 0

# Write header
with open(dms_rot_filepath, 'wb') as file:
    file.writelines(header_rot_lines)
offset += sum([len(line) for line in header_rot_lines])
# Write images
out = np.memmap(
    dms_rot_filepath,
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
with open(dms_rot_filepath, 'ab') as file:
    # file.seek(offset)
    file.writelines(names_lines)

# Save images
image_paths = [
    dms_rot_filepath.parent / f"{dms_rot_filepath.stem}_{''.join(name.split())}.png"
    for name in names
]
for i, path in zip(range(images_rot.shape[0]), image_paths):
    save_dms_image(images_rot[i, :, :], path, 16)
