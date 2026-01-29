"""Model."""

from pathlib import Path

from raw_rpl_dms_tools.signaler import Signaler
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
        self.rotate_turns = 0
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
    def rotate_turns(self) -> int:
        """Amount of 90-degree turns to rotate."""
        return self._rotate_turns

    @rotate_turns.setter
    def rotate_turns(self, turns: int) -> None:
        self._rotate_turns = turns
        self._signal(turns)

    @property
    def overwrite(self) -> bool:
        """Whether to overwrite existing files."""
        return self._overwrite

    @overwrite.setter
    def overwrite(self, overwrite: bool) -> None:
        self._overwrite = overwrite
        self._signal(overwrite)

    def generate_preview(self) -> PathOrNone:
        """Generate a preview PNG image of the RAW-RPL pair."""
        if not self.raw_filepath:
            raise Exception("RAW file not defined.")
        if not self.rpl_filepath:
            raise Exception("RPL file not defined.")
        filepath = make_raw_preview(
            self.raw_filepath,
            self.rpl_filepath,
            show=True
        )
        self._signal(filepath)
        return filepath

    def transform_and_save_copy(self) -> tuple[PathOrNone, PathOrNone]:
        """Transform and save a copy of the RAW-RPL pair."""
        if not self.raw_filepath:
            raise Exception("RAW file not defined.")
        if not self.rpl_filepath:
            raise Exception("RPL file not defined.")
        return rot90_raw_rpl(
            raw_filepath=self.raw_filepath,
            rpl_filepath=self.rpl_filepath,
            n=self.rotate_turns,
            mode="x",  # Raise if exists
        )
