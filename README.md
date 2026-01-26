# RAW RPL Tools

User interface to preview and rotate RAW RPL (Ripple) file pairs of MA-XRF spectral data.

Built with Python and a modified, stripped-down version of [`maxrf4u`](https://github.com/fligt/maxrf4u) package by [Frank Ligterink](https://github.com/fligt).

Available for macOS and Windows at just under 20 MB.

TODO: Screenshot


## TODO: Download and run

### Windows

### macOS


## TODO: Features

### Preview

### Rotate

## TODO: Developers

RAW RPL Tools runs on Python 3.14 with a just a couple [dependencies](#dependencies).

### Dependencies

### Install

```bash
poetry install
```



### Windows executable

```
pyinstaller --onefile --windowed --recursive-copy-metadata raw_rpl_tools --icon=icon.ico --add-data=C:\art\raw-rpl-tools\src\raw_rpl_tools\icon.ico:. .\main.py
```

### macOS package

```bash
cd src/raw_rpl_tools
pyinstaller --onefile --windowed script.py -y 
```


## TODO: Avoid Windows Defender SmartScreen

## TODO: Credits

Created by Lars Maxfield

maxrf4u Copyright (c) 2026 Frank Ligterink with modifications by Lars Maxfield

[Icon](https://icon-icons.com/icon/atom/96146) by [Good Stuff Non Sense](https://goodstuffnononsense.com/), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
