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

# 'w' open for writing, truncating the file first
# 'x' open for exclusive creation, failing if the file already exists
WriteMode = Literal['w', 'x']

# # # CONSTANTS
# # DATASTACK_EXT = '.datastack'


# # # COMPUTION ORDER
# # class Layers:

# #     def __init__(self):

# #         self.LAYERS = ['MAXRF_CUBE',
# #                        'MAXRF_MAXSPECTRUM',
# #                        'MAXRF_SUMSPECTRUM',
# #                        'MAXRF_ENERGIES',
# #                        'HOTMAX_PIXELS',
# #                        'HOTMAX_SPECTRA',
# #                        'HOTMAX_BASELINES',
# #                        'HOTMAX_NOISELINES',
# #                        'MAPS_IMVIS']

# #         for l in self.LAYERS:
# #             setattr(self, l, l.lower())

# # L = Layers()


# # # functions

# # def raw_to_datastack(raw_file, rpl_file, sigma=7, output_dir=None, name=L.MAXRF_CUBE, verbose=True,
# #                     flip_horizontal=False, flip_vertical=False, chunks='10 MiB', rechunk=False):
# #     '''Convert Bruker Macro XRF (.raw) data file `raw_filename` and (.rpl) shape file `rpl_filename`.

# #     into a zarr ZipStore datastack file (.datastack).

# #     To avoid memory problems on computers with less RAM the chunks option is set to '10 MiB'.
# #     '''

# #     print('Please wait while preparing data conversion...')

# #     # generate datastack file path from raw_file and output_dir
# #     if output_dir is None:
# #         # save in same folder
# #         datastack_file = re.sub('\\.raw$', '', raw_file) + DATASTACK_EXT

# #     else:
# #         # save in output folder
# #         assert os.path.exists(output_dir),  'Can not save to non-existing directory.'
# #         basename = os.path.basename(raw_file)
# #         basename = re.sub('\\.raw$', '', basename) + DATASTACK_EXT
# #         datastack_file = os.path.join(output_dir, basename)

# #     # read data cube shape and dtype from .rpl file
# #     dtype, shape = parse_rpl(rpl_file, verbose=verbose)

# #     # create numpy memory map with proper orientation
# #     v_stride = 1
# #     h_stride = 1
# #     if flip_vertical:
# #         v_stride = -1
# #     if flip_horizontal:
# #         h_stride = -1

# #     print('Creating memory map...')
# #     raw_mm = np.memmap(raw_file, dtype=dtype, mode='r', shape=shape)[::v_stride, ::h_stride]

# #     # initializing dask array
# #     arr = da.from_array(raw_mm, chunks=chunks)
# #     arr = arr.astype(np.float32)


# #     # divide into regular chunks
# #     if rechunk:
# #         arr = arr.rechunk(balance=True)

# #     # schedule spectral gaussian smoothing computation
# #     if sigma == 0:
# #         smoothed = arr
# #     else:
# #         smoothed = gaussian_filter(arr, (0, 0, sigma))

# #     # create and open an empty zip store
# #     zs = ZipStore(datastack_file, mode='w')

# #     if verbose:
# #         print(f'Writing: {datastack_file}...')

# #     # compute and write maxrf data to zipstore
# #     with ProgressBar():

# #         # smoothed.to_zarr(zs, component=datapath) # broken due to dask.to_zarr bug
# #         #zarr.create_array(store=zs, name=name, data=arr) # forgot to use smoothed instead of arr!
# #         zarr.create_array(store=zs, name=name, data=smoothed) # this should be better

# #         # updating dask to version 2025.12.0
# #         # should fix the previous dask.to_zarr bug
# #         # and make computing faster (I hope this works...)
# #         # IT DOES NOT SO REVERTING TO above code
# #         #smoothed.to_zarr(zs, component=name)

# #     zs.close()


# #     # also compute sum and max spectra and append to zipstore

# #     y_max, y_sum = max_and_sum_spectra(datastack_file, datapath=L.MAXRF_CUBE, chunks=chunks)

# #     append(y_max, L.MAXRF_MAXSPECTRUM, datastack_file)
# #     append(y_sum, L.MAXRF_SUMSPECTRUM, datastack_file)

# #     print('\n')

# #     return datastack_file


# # def tree(datastack_file, show_arrays=False):
# #     '''Prints content tree of *datastack_file* '''

# #     with ZipStore(datastack_file) as zs:
# #         root = zarr.open_group(store=zs, mode='r')
# #         tree = root.tree().__repr__() # removed expand=True for now
# #         print(f'{datastack_file}:\n\n{tree}')

# #         if show_arrays:
# #             datasets = sorted(root)
# #             arrays_html = ''

# #             for ds in datasets:
# #                 arr = da.from_array(root[ds])
# #                 html = arr._repr_html_()
# #                 arrays_html = f'{arrays_html}- Dataset: <h style="color:brown">{ds}</h>{html}'

# #             return HTML(arrays_html)

# # def underscorify(datapath, datapath_list, extra_underscore=True):
# #     '''Append extra underscore if *datapath* exists to prevent overwriting.

# #     If *extra_underscore=False* return (latest) datapath with most underscores'''

# #     if datapath in datapath_list:
# #         r = re.compile(f'{datapath}_*$')
# #         datapath = sorted(filter(r.match, datapath_list))[-1]

# #         if extra_underscore:
# #             datapath = datapath + '_'

# #     return datapath


# # def append(arr, datapath, datastack_file):
# #     '''Add numpy or dask array *arr* to *datastack_file* in folder *datapath*.'''

# #     if not isinstance(arr, dask.array.Array):
# #         arr = da.from_array(arr)

# #     zs = ZipStore(datastack_file, mode='a')
# #     root = zarr.open_group(store=zs) # ehm, I need a listing of all datasets

# #     # append underscores to make unique if datapath exists
# #     datapath_list = sorted(root)
# #     datapath = underscorify(datapath, datapath_list)

# #     # write to datastack
# #     zarr.create_array(store=zs, name=datapath, data=arr)
# #     zs.close()

# #     # old code using dask but not working
# #     #arr.to_zarr(zs, component=datapath)


# # def append_list(ragged_list, datapath, datastack_file, nan=-9999):
# #     '''Wrapper around append() to store iregular (ragged) lists of lists as regular padded arrays.

# #     Currently only working for two dimensional lists of integers. Padding is done with nan=-9999.
# #     '''

# #     padded_array = _straighten(ragged_list, nan=nan)

# #     append(padded_array, datapath, datastack_file)


# # def repack(datastack_file, select='all', overwrite=True, verbose=False):
# #     '''Repack *datastack_file* by deleting and renaming all but latest datasets.

# #     Automatic selection of latest datasets can be overriden be providing list of *select* datasets'''

# #     if verbose:
# #         tree(datastack_file)

# #     # open existing zipstore
# #     zs = ZipStore(datastack_file)
# #     root = zarr.open_group(store=zs, mode='r')
# #     datapath_list = sorted(root)

# #     # select newest version (most underscores) for all datasets
# #     if select == 'all':
# #         selected = sorted(set([underscorify(dp, datapath_list, extra_underscore=False) for dp in datapath_list]))
# #     # select newest version (most underscores) for datasets in select
# #     else:
# #         selected = sorted(set([underscorify(dp, datapath_list, extra_underscore=False) for dp in select]))

# #     # remove underscores
# #     renamed = [re.sub('_*$', '', s) for s in selected]

# #     # create and open new empty zipstore
# #     datastack_file_new = datastack_file + '_temp'
# #     zs_new = ZipStore(datastack_file_new, mode='w')

# #     # copy selected datasets into new zipstore
# #     with ProgressBar():
# #         for src, dst in zip(selected, renamed):
# #             print(f'Repacking dataset: \'{src}\'')
# #             arr = da.from_array(root[src])
# #             arr.to_zarr(zs_new, component=dst)

# #     zs.close()
# #     zs_new.close()

# #     # finally overwrite old with new
# #     if overwrite:
# #         os.replace(datastack_file_new, datastack_file)

# #     if verbose:
# #         print()
# #         tree(datastack_file)


# # def max_and_sum_spectra(datastack_file, datapath=L.MAXRF_CUBE, chunks="auto"):
# #     '''Compute sum spectrum and max spectrum for 'maxrf' dataset in *datastack_file*.

# #     Returns: *y_sum*, *y_max*'''

# #     # open existing zipstore
# #     zs = ZipStore(datastack_file)
# #     root = zarr.open_group(store=zs, mode='r')

# #     # initialize dask array
# #     arr = da.from_array(root[datapath], chunks=chunks)

# #     # flatten (better avoid)
# #     h, w, d = arr.shape
# #     #flat_shape = h * w, d
# #     #with dask.config.set(**{'array.slicing.split_large_chunks': True}):
# #     #    arr_flat = arr.reshape(flat_shape) #, limit='128 MiB')
# #     #
# #     ## schedule computations
# #     #sum_spectrum = arr_flat.sum(axis=0)
# #     #max_spectrum = arr_flat.max(axis=0)
# #     sum_spectrum = arr.sum(axis=(0, 1))
# #     max_spectrum = arr.max(axis=(0, 1))

# #     # compute
# #     print('Computing max spectrum...')
# #     with ProgressBar():
# #         y_max = max_spectrum.compute()
# #     print('Computing sum spectrum...')
# #     with ProgressBar():
# #         y_sum = sum_spectrum.compute() / (h * w)

# #     zs.close()

# #     return y_max, y_sum


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
            "Line does not match " \
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


# # class DataStack:

# #     def __init__(self, datastack_file, mode='r', verbose=False, show_arrays=True):
# #         '''Initialize DataStack object from *datastack_file*.'''

# #         # default computation layers ordering as attributes

# #         self.LAYERS = L.LAYERS

# #         for l in L.LAYERS:
# #             setattr(self, l, l.lower())

# #         # read datasets from file

# #         self.mode = mode
# #         self.datastack_file = datastack_file

# #         self.update_attrs()

# #         # print tree
# #         if verbose:
# #             tree(self.datastack_file, show_arrays=show_arrays)

# #     def update_attrs(self):

# #         # populate store attributes
# #         self.store = ZipStore(self.datastack_file)
# #         self.root = zarr.open_group(store=self.store, mode=self.mode)

# #         # generic exposure to dask arrays
# #         self.datapath_list = sorted(self.root)
# #         self.datasets = {dp: da.from_array(self.root[dp]) for dp in self.datapath_list}

# #         # attributify dask arrays
# #         # useful for code development, perhaps confusing for users
# #         # might turn off this feature later
# #         for dp, ds in self.datasets.items():
# #             setattr(self, dp, ds)


# #     def latest(self, datapath):
# #         '''Return latest version of datapath. '''

# #         datapath = underscorify(datapath, self.datapath_list, extra_underscore=False)

# #         return datapath


# #     def read(self, datapath, latest=True, compute=True):
# #         '''Read latest version of dataset for *datapath*

# #         Returns numpy array if dataset exists. Otherwise exits. '''

# #         if datapath in self.datapath_list:
# #             if latest:
# #                 datapath = self.latest(datapath)
# #             dataset = self.datasets[datapath]
# #             if compute:
# #                 dataset = dataset.compute()

# #         # no dataset in file
# #         else:
# #             dataset = None

# #             self.tree()
# #             assert False, f'Dataset not found: {datapath}'

# #         return dataset


# #     def read_list(self, datapath, latest=True, nan=-9999):
# #         '''Thin wrapper for reading padded arrays (ragged lists).

# #         Returns ragged list if dataset exists. Current implementation only for
# #         two-dimensional (ragged) list of lists. '''

# #         # step 1: read (padded array
# #         padded_array = self.read(datapath, latest=latest, compute=True)

# #         # step 2: convert to ragged list by removing nan values
# #         ragged_list = _unstraighten(padded_array, nan=nan)

# #         return ragged_list


# #     def tree(self, show_arrays=False):
# #         '''Prints content tree of datastack.'''

# #         tree(self.datastack_file, show_arrays=show_arrays)


# #     def close(self):
# #         '''Close file handle'''

# #         self.store.close()
# #         self.mode = 'closed'

# #         print(f'Closed: {self.datastack_file}')

# # def _straighten(ragged_list, nan=-9999):
# #     '''Utility function to straighten a `ragged_list` of integers indices into a regular (padded) array.


# #     Creates a two dimensional numpy array with empty values padded with nan=-9999.

# #     Returns: padded_array
# #     '''

# #     # determine shape
# #     ncols = max([len(idxs) for idxs in ragged_list])
# #     nrows = len(ragged_list)

# #     # initialize
# #     padded_array = np.ones([nrows, ncols], dtype=int)
# #     padded_array[:,:] = nan

# #     # fill

# #     for i, indices in enumerate(ragged_list):
# #         for j, idx in enumerate(indices):
# #             padded_array[i, j] = idx

# #     return padded_array


# # def _unstraighten(padded_array, nan=-9999):
# #     '''Convert a numpy `padded_array` of integers filled out with nan's into a ragged list.


# #     Returns: a ragged list of lists
# #     '''

# #     ragged_list = []

# #     for row in padded_array:
# #         row_list = list(row[row!=nan]) # remove nan's from list
# #         ragged_list.append(row_list)

# #     return ragged_list
