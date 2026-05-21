from pathlib import Path
from kinai.core.types import Dirs, Files

ROOT_PATH = Path(__file__).resolve().parents[3]

class Paths:
    def __init__(self, root: Path | None = None):
        self.root = root or ROOT_PATH

    @property
    def base(self) -> Path:
        return self.root / Dirs.corpora.value

    @property
    def annotations(self) -> Path:
        return self.base / Dirs.ann.value

    # ---- FILES ----
    @property
    def source_segments(self) -> Path:
        return self.annotations / Files.source.value

    @property
    def align_manifest(self) -> Path:
        return self.annotations / Files.ali_man.value

    @property
    def long_sources(self) -> Path:
        return self.annotations / Files.long_srcs.value

    @property
    def data_manifest(self) -> Path:
        return self.annotations / Files.data_man.value

    @property
    def yt_audio_folder(self) -> Path:
        return self.root / Dirs.assets.value / Dirs.yt_audio.value

    @property
    def assets_folder(self) -> Path:
        return self.root / Dirs.assets.value

    @property
    def segments_folder(self) -> Path:
        return self.root / Dirs.assets.value / Dirs.segmented_audio.value

    @property
    def kaldi_root(self) -> Path:
        return self.root / "kaldi"

    # ---- SHARED (cross-iteration) ----
    @property
    def corpora_root(self) -> Path:
        return self.root / Dirs.corpora.value

    @property
    def iterations_root(self) -> Path:
        return self.corpora_root / Dirs.iterations.value

    @property
    def shared_dir(self) -> Path:
        return self.corpora_root / Dirs.shared.value

    @property
    def shared_lexicon_dir(self) -> Path:
        return self.shared_dir / Dirs.lexicon.value

    @property
    def text_assets_dir(self) -> Path:
        return self.assets_folder / Dirs.text.value

    # ---- KALDI RECIPE ----
    @property
    def recipe_dir(self) -> Path:
        return self.base / Dirs.kaldi.value

    @property
    def kaldi_data(self) -> Path:
        return self.recipe_dir / "data"

    @property
    def kaldi_train(self) -> Path:
        return self.kaldi_data / "train"

    @property
    def kaldi_align(self) -> Path:
        return self.kaldi_data / "align"

    @property
    def kaldi_local_lang(self) -> Path:
        return self.kaldi_data / "local" / "lang"
