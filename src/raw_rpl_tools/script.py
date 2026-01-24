"""Test script."""

import os
import tkinter as tk
from pathlib import Path

import numpy as np
import png

from maxrf4u_lite.storage import make_raw_preview, rot90_raw_rpl

base: Path = Path('/Users/max/Developer/data/xrf/spectral-datacube')
raw_filepath: Path = Path(f'{base}.raw')
rpl_filepath: Path = Path(f'{base}.rpl')
# output: Path = Path('/Users/max/Developer/data/')
output_dirpath = None

# make_raw_preview(raw, rpl, output, show=True, save=True, verbose=True)
rot90_raw_rpl(raw_filepath, rpl_filepath, output_dirpath, 0)

# # Create the main window
# root = tk.Tk()
# root.title("Simple App")

# # Add a label
# label = tk.Label(root, text="Hello, Tkinter!")
# label.pack(pady=10)

# # Add a button that closes the app
# button = tk.Button(root, text="Close", command=root.destroy)
# button.pack(pady=10)

# print(maxrf4u_lite)

# image = np.ones([200, 300])
# image *= 255

# path = Path('image.png')  # /Users/max/image.png
# print(f'Absolute: {path.absolute()}')

# try:
#     png.from_array(image.astype(np.uint8), mode='L;8').save(path)
# except Exception as e:
#     print(e)
# print(os.path.dirname(os.path.realpath(__file__)))

# # Run the application
# root.mainloop()
