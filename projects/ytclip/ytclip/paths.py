"""Rutas que usa ytclip.

Envoltorio fino sobre `mayanlab.paths`, que es la definición única del
repositorio. `Paths` existe solo para que los módulos que ya recibían un objeto
`paths` sigan funcionando; los valores vienen todos de `mayanlab`.
"""

from pathlib import Path

from mayanlab import paths as _p

REPO_ROOT = _p.REPO_ROOT


class Paths:
    """Vista de las rutas del proyecto relevantes para ytclip."""

    def __init__(self, root: Path | None = None):
        self.root = root or _p.REPO_ROOT

    # --- audio ---
    @property
    def segments_folder(self) -> Path:
        """Destino de los recortes: data/work/segments/."""
        return _p.SEGMENTS

    @property
    def yt_audio_folder(self) -> Path:
        """Audio completo descargado de YouTube: data/source/youtube/."""
        return _p.YOUTUBE

    @property
    def corpus_audio(self) -> Path:
        """Corpus canónico ya nombrado por utt_id: data/final/audio/."""
        return _p.AUDIO

    # --- anotaciones y manifiestos ---
    @property
    def annotations(self) -> Path:
        return _p.ANNOTATIONS

    @property
    def manifests(self) -> Path:
        return _p.MANIFESTS

    @property
    def source_segments(self) -> Path:
        return _p.MANIFESTS / "source_segments.json"
