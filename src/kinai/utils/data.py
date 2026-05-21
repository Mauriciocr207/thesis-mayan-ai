from pathlib import Path

def get_project_root(marker=".git"):
    """Busca el directorio raíz del proyecto basado en un marcador (por ejemplo, .git o pyproject.toml)."""
    current = Path(__file__).resolve().parent
    for parent in current.parents:
        if (parent / marker).exists():
            return parent
    return Path.cwd()

def get_audios_dir():
    return get_project_root() / "data/audios/"