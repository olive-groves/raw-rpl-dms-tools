"""Model."""

from pathlib import Path

from raw_rpl_tools.signaler import Signaler
from maxrf4u_lite.storage import make_raw_preview, rot90_raw_rpl

PathOrNone = Path | None


class RawRplModel(Signaler):
    """maxrf4u_lite functions bundled as a model."""
    def __init__(self) -> None:
        super().__init__()
        self.observers = []
        self.initialize()

    def initialize(self) -> None:
        """Initialize model."""
        self.raw_filepath = None
        self.rpl_filepath = None
        self.rotate_degrees = 0
        self.overwrite = False
        return

    @property
    def raw_filepath(self) -> PathOrNone:
        """File path to RAW file."""
        return self._raw_filepath

    @raw_filepath.setter
    def raw_filepath(self, path: PathOrNone) -> None:
        if path and not path.is_file():
            raise FileNotFoundError("File does not exist.")
        self._raw_filepath = path
        self._signal(path)

    @property
    def rpl_filepath(self) -> PathOrNone:
        """File path to RPL file."""
        return self._rpl_filepath

    @rpl_filepath.setter
    def rpl_filepath(self, path: PathOrNone) -> None:
        if path and not path.is_file():
            raise FileNotFoundError("File does not exist.")
        self._rpl_filepath = path
        self._signal(path)

    @property
    def rotate_degrees(self) -> int:
        """Amount of degrees to rotate."""
        return self._rotate_degrees

    @rotate_degrees.setter
    def rotate_degrees(self, degrees: int) -> None:
        self._rotate_degrees = degrees
        self._signal(degrees)

    @property
    def overwrite(self) -> bool:
        """Whether to overwrite existing files."""
        return self._overwrite

    @overwrite.setter
    def overwrite(self, overwrite: bool) -> None:
        self._overwrite = overwrite
        self._signal(overwrite)

    def generate_preview(self):
        # TODO: Check RAW, RPL exist
        filepath = make_raw_preview(
            self.raw_filepath,
            self.rpl_filepath,
            show=True
        )
        self._signal(filepath)
