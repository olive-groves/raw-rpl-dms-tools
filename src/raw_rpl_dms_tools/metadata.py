"""Metadata."""

from pathlib import Path
import re
import importlib.metadata
import raw_rpl_dms_tools


def parse_project_url(project_url: list[str]) -> dict:
    """Parse the URLS of a project_url from importlib.metadata.metadata().json, v2.4."""
    return dict(string.split(', ', 1) for string in project_url)


def parse_files(files: list[importlib.metadata.PackagePath]) -> dict:
    """Parse the files from importlib.metadata.files()."""
    return {path.name: path for file in files if (path := Path(file))}


TITLE = "RAW-RPL DMS Tools"
NAME = raw_rpl_dms_tools.__name__

_metadata = importlib.metadata.metadata(NAME).json

_files = parse_files(importlib.metadata.files(NAME) or [])

_project_urls_get = _metadata.get("project_url", "")
if isinstance(_project_urls_get, str):
    _project_urls_get = [_project_urls_get]
_project_urls = parse_project_url(_project_urls_get)

VERSION = _metadata.get("version", "version undefined")
SUMMARY = _metadata.get("summary", "summary undefined")
AUTHOR = _metadata.get("author", "author undefined")
LICENSE = _metadata.get("license_expression", "license undefined")

HOMEPAGE = _project_urls.get("Homepage", "homepage undefined")

LICENSE_FILE = "license file undefined"
_license_filepath: Path | None = _files.get("LICENSE", None)
if _license_filepath:
    try:
        with open(_license_filepath, 'r') as file:
            LICENSE_FILE = file.read()
    except Exception as e:
        print(f"Unexpected error attempting to read {_license_filepath}: {e}.")
LICENSE_FILE = text = re.sub(r'(?<!\n)\n(?!\n)', ' ', LICENSE_FILE)
