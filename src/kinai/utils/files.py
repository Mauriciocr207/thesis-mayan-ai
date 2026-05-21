import re
from pathlib import Path

def create_dir(path: Path):
    """Crea un directorio si no existe."""
    path.mkdir(parents=True, exist_ok=True)
    
def natural_sort_key(s: str):
    """Clave para ordenar nombres de archivos de manera numérica (1,2,3,...10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]