"""Test script."""

import tkinter as tk
from pathlib import Path

from maxrf4u_lite.storage import make_raw_preview, rot90_raw_rpl

# base: Path = Path('/Users/max/Developer/data/xrf/spectral-datacube')
# raw_filepath: Path = Path(f'{base}.raw')
# rpl_filepath: Path = Path(f'{base}.rpl')
# # output: Path = Path('/Users/max/Developer/data/')
# output_dirpath = None

# # make_raw_preview(raw_filepath, rpl_filepath, show=True)

# rot_raw_filepath, rot_rpl_filepath = (
#     rot90_raw_rpl(raw_filepath, rpl_filepath, output_dirpath, 3, 'x')
# )
# make_raw_preview(rot_raw_filepath, rot_rpl_filepath, show=True)


# Create the main window
root = tk.Tk()
root.title("Simple App")

# Add a label
label = tk.Label(root, text="Hello, Tkinter!")
label.pack(pady=10)

# Add a button that closes the app
button = tk.Button(root, text="Close", command=root.destroy)
button.pack(pady=10)

# Run the application
root.mainloop()
