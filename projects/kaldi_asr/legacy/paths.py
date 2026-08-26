"""Rutas de la etapa Kaldi. ARCHIVADO.

Este módulo mantiene el objeto `Paths` que esperaba el pipeline de Kaldi, ahora
resuelto sobre la estructura nueva de `data/` (ver `mayanlab.paths`). Se conserva
para que el archivo sea autocontenido y se pueda revivir sin reconstruirlo desde
cero; no está en uso.
"""

from pathlib import Path

from mayanlab import paths as _p


class Paths:
    def __init__(self, iter_id: str = "01", root: Path | None = None):
        self.root = root or _p.REPO_ROOT
        self.iter_id = iter_id

    # --- receta ---
    @property
    def recipe_dir(self) -> Path:
        return _p.PROJECTS / "kaldi_asr" / "recipe"

    @property
    def kaldi_root(self) -> Path:
        return _p.KALDI_ROOT

    @property
    def kaldi_data(self) -> Path:
        return self.recipe_dir / "data"

    @property
    def kaldi_local_lang(self) -> Path:
        return self.kaldi_data / "local" / "lang"

    @property
    def iterations_root(self) -> Path:
        return self.recipe_dir / "iterations"

    @property
    def shared_lexicon_dir(self) -> Path:
        return _p.PROJECTS / "kaldi_asr" / "lexicon"

    # --- datos ---
    @property
    def annotations(self) -> Path:
        return _p.ANNOTATIONS

    @property
    def segments_folder(self) -> Path:
        return _p.SEGMENTS

    @property
    def text_assets_dir(self) -> Path:
        return _p.LM_TEXT

    @property
    def source_segments(self) -> Path:
        """Manifiesto en el formato ANTIGUO, con maya/spanish."""
        return _p.PROJECTS / "kaldi_asr" / "legacy" / "annotations" / "source_segments.json"

    @property
    def align_manifest(self) -> Path:
        return _p.MANIFESTS / "align_manifest.csv"

    @property
    def data_manifest(self) -> Path:
        return _p.MANIFESTS / "data_manifest.csv"

    @property
    def long_sources(self) -> Path:
        return _p.MANIFESTS / "long_sources.json"
