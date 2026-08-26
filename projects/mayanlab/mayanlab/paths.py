"""Definición única de rutas del proyecto.

Todo el repositorio —notebooks, scripts y el CLI `ytclip`— resuelve sus rutas
desde aquí. No hay rutas relativas al directorio de trabajo en ningún otro
sitio, así que da igual desde dónde se ejecute un notebook o un script.

La raíz de datos es `<repo>/data` salvo que se defina `MAYAN_DATA` (en `.env` o
en el entorno), lo que permite apuntar a otro disco o, en Colab, a Drive:

    import os
    os.environ["MAYAN_DATA"] = "/content/drive/MyDrive/thesis-mayan-ai/data"
    from mayanlab.paths import AUDIO

La organización de `data/` distingue lo que vino de fuera (`source/`) de lo que
produce el proyecto (`final/`), con `work/` para lo regenerable y desechable.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "REPO_ROOT", "DATA", "SOURCE", "WORK", "FINAL",
    "YOUTUBE", "NARRACIONES", "NARRACIONES_MP3", "NARRACIONES_TRANSCRIPTS",
    "RECORDINGS", "GLOBAL_RECORDINGS", "MMS", "ANNOTATIONS",
    "SEGMENTS", "CLEAN_TEXT", "ORPHAN_SEGMENTS",
    "AUDIO", "TRANSCRIPTS", "LM_TEXT", "MANIFESTS",
    "PROJECTS", "TOOLS", "KALDI_ROOT", "KENLM_BIN",
    "ProjectDirs", "project", "ensure",
]


def _find_repo_root() -> Path:
    """Sube desde este archivo hasta el directorio que contiene el pyproject.toml."""
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "pyproject.toml").is_file():
            return candidate
    # Paquete instalado fuera del repo (p. ej. en Colab): sin repo que anclar.
    return Path.cwd()


REPO_ROOT = _find_repo_root()


def _load_dotenv() -> None:
    """Carga <repo>/.env sin pisar variables ya definidas en el entorno."""
    env_file = REPO_ROOT / ".env"
    if not env_file.is_file():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(env_file, override=False)


_load_dotenv()

_data_override = os.getenv("MAYAN_DATA", "").strip()
DATA = Path(_data_override).expanduser().resolve() if _data_override else REPO_ROOT / "data"

# --- fuente: lo que vino de fuera, nunca se edita ---------------------------
SOURCE = DATA / "source"
YOUTUBE = SOURCE / "youtube"
NARRACIONES = SOURCE / "narraciones_inali"
NARRACIONES_MP3 = NARRACIONES / "mp3"
NARRACIONES_TRANSCRIPTS = NARRACIONES / "transcripts"
RECORDINGS = SOURCE / "recordings"
GLOBAL_RECORDINGS = SOURCE / "global_recordings_net"
MMS = SOURCE / "mms"
ANNOTATIONS = SOURCE / "annotations"

# --- work: regenerable y desechable ----------------------------------------
WORK = DATA / "work"
SEGMENTS = WORK / "segments"
CLEAN_TEXT = WORK / "narraciones_clean_text"
ORPHAN_SEGMENTS = WORK / "orphan_segments"

# --- final: lo que produce el proyecto -------------------------------------
FINAL = DATA / "final"
AUDIO = FINAL / "audio"
TRANSCRIPTS = FINAL / "transcripts"
LM_TEXT = FINAL / "lm_text"
MANIFESTS = FINAL / "manifests"

# --- código y herramientas --------------------------------------------------
PROJECTS = REPO_ROOT / "projects"
TOOLS = REPO_ROOT / "tools"
KALDI_ROOT = TOOLS / "kaldi"
KENLM_BIN = TOOLS / "kenlm" / "build" / "bin"


@dataclass(frozen=True)
class ProjectDirs:
    """Carpetas de un proyecto de `projects/`."""

    name: str

    @property
    def root(self) -> Path:
        return PROJECTS / self.name

    @property
    def notebooks(self) -> Path:
        return self.root / "notebooks"

    @property
    def scripts(self) -> Path:
        return self.root / "scripts"

    @property
    def figures(self) -> Path:
        return self.root / "figures"

    @property
    def features(self) -> Path:
        return self.root / "features"

    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def results(self) -> Path:
        return self.root / "results"


def project(name: str) -> ProjectDirs:
    """Carpetas del proyecto `name` (p. ej. `project("analysis").figures`)."""
    return ProjectDirs(name)


def ensure(*paths: Path) -> None:
    """Crea los directorios que falten. Útil antes de escribir salidas."""
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
