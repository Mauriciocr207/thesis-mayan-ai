"""Normaliza los textos de `narraciones_mayas_campeche/text/*.txt`.

Elimina cabeceras de página, números de página, artefactos de extracción de PDF
(nombres de ponente partidos en varias líneas, líneas en blanco que rompen
párrafos) y devuelve un `.tsv` con columnas `speaker\ttext` por utterance.

Salida: `data/work/narraciones_clean_text/<base>.tsv`

Uso:
    python projects/kaldi_asr/scripts/normalize_narraciones.py
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

from mayanlab.paths import CLEAN_TEXT, NARRACIONES_TRANSCRIPTS
from mayanlab.tokenizer import modernize_orthography, normalize_word

SRC_DIR = NARRACIONES_TRANSCRIPTS
OUT_DIR = CLEAN_TEXT

HEADERS = {"Narraciones Mayas de Campeche", "Maayáaj Tsikbalilo'ob Kaampech"}

# Un fragmento corto con letras (no dígitos solos) seguido de `:` al final.
# Admite espacios internos (p.ej. "Venus T iano:" tras unir las líneas rotas).
SPEAKER_RE = re.compile(r"^([A-Za-zÁÉÍÓÚáéíóúñÑ][A-Za-zÁÉÍÓÚáéíóúñÑ ]{0,30}):\s*(.*)$")
PAGE_NUM_RE = re.compile(r"^\d{1,4}$")
# Apóstrofos tipográficos que debemos reducir a ' (ASCII) porque el tokenizer
# usa apóstrofo recto.
APOSTROPHES = "\u2019\u2018\u02bc\u02bb\u055a"


def _fix_apostrophes(text: str) -> str:
    for ch in APOSTROPHES:
        text = text.replace(ch, "'")
    return text


def _merge_broken_speakers(lines: list[str]) -> list[str]:
    """Une líneas sueltas que solo contienen fragmentos cortos capitalizados
    y son seguidas de `:` (artefacto de extracción en columnas).
    Ej: ["Venus", "T", "iano:"] → ["VensTiano:"] (lo normalizamos luego).
    """
    merged: list[str] = []
    buf: list[str] = []

    def flush_buf():
        if buf:
            merged.append("".join(buf))
            buf.clear()

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_buf()
            merged.append("")
            continue
        # Fragmento corto capitalizado sin `:` al final → parte de nombre partido.
        is_name_chunk = (
            len(stripped) <= 8
            and stripped[0].isalpha()
            and stripped[0].isupper()
            and ":" not in stripped
            and " " not in stripped
            and not any(ch.isdigit() for ch in stripped)
        )
        # La línea que cierra el nombre: termina con `:` y viene tras fragmentos.
        closes_name = stripped.endswith(":") and len(stripped) <= 12 and buf
        if is_name_chunk:
            buf.append(stripped)
            continue
        if closes_name:
            buf.append(stripped)
            merged.append("".join(buf))
            buf.clear()
            continue
        flush_buf()
        merged.append(line)
    flush_buf()
    return merged


def _merge_speaker_only_lines(lines: list[str]) -> list[str]:
    """Une `Nombre:` que aparece solo en una línea con la siguiente línea no
    vacía — formato usado por los archivos donde el texto está separado del
    tag por una línea en blanco (p.ej. 13_Venustiano_Puc)."""
    out: list[str] = []
    pending: str | None = None
    for raw in lines:
        s = raw.strip()
        if not s:
            if pending is None:
                out.append(raw)
            continue
        m = SPEAKER_RE.match(s)
        if m and not m.group(2).strip() and pending is None:
            pending = s  # "Nombre:"
            continue
        if pending:
            out.append(f"{pending} {s}")
            pending = None
        else:
            out.append(raw)
    if pending:
        out.append(pending)
    return out


def _group_paragraphs(lines: list[str]) -> list[str]:
    """Agrupa líneas consecutivas en párrafos.

    Crea un corte de párrafo cuando:
      - Hay una línea en blanco.
      - La siguiente línea comienza con un tag de ponente (`Nombre:`) —
        soporta archivos que no usan líneas en blanco entre turnos (p.ej. 09).
    """
    paragraphs: list[str] = []
    buf: list[str] = []

    def flush():
        if buf:
            paragraphs.append(" ".join(buf))
            buf.clear()

    for line in lines:
        s = line.strip()
        if not s:
            flush()
            continue
        if s in HEADERS:
            continue
        if PAGE_NUM_RE.match(s):
            continue
        if SPEAKER_RE.match(s):
            flush()
        buf.append(s)
    flush()
    return paragraphs


def _split_paragraph_utterances(paragraph: str) -> list[tuple[str | None, str]]:
    """Divide un párrafo en utterances.

    Reconoce:
      - Prefijo de ponente al inicio: `Nombre: texto...`
      - Turnos de diálogo marcados con em-dash `—` dentro del texto.
    """
    out: list[tuple[str | None, str]] = []
    text = paragraph

    m = SPEAKER_RE.match(text)
    speaker: str | None = None
    if m:
        speaker = _clean_speaker_name(m.group(1))
        text = m.group(2).strip()
    if not text:
        return out
    # Los turnos de diálogo con — se añaden como utterances sin ponente asignado
    # (son citas directas dentro del monólogo del mismo ponente).
    parts = [p.strip() for p in re.split(r"\s*—\s*", text) if p.strip()]
    for i, part in enumerate(parts):
        spk = speaker if i == 0 else (f"{speaker}::quote" if speaker else "::quote")
        out.append((spk, part))
    return out


def _clean_speaker_name(name: str) -> str:
    compact = re.sub(r"\s+", "", name)
    # Normaliza capitalización (p.ej. feLipe → Felipe, HéCTor → Héctor).
    return compact[:1].upper() + compact[1:].lower() if compact else compact


_KEEP_CHARS = set("abcdefghijklmnopqrstuvwxyzáéíóúñ' ")


def _normalize_text(text: str) -> str:
    """Minúsculas, quita puntuación no léxica y normaliza apóstrofos.

    Preserva el apóstrofo `'` porque es fonema (glotal) en maya.
    """
    text = _fix_apostrophes(text)
    # NFC para asegurar composición canónica de acentos.
    text = unicodedata.normalize("NFC", text)
    # Reemplaza cualquier espacio/guión por un espacio simple.
    text = re.sub(r"[\t\r\n]+", " ", text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[–—]", " ", text)
    words_out: list[str] = []
    for w in text.split():
        w = normalize_word(w)
        if not w:
            continue
        w = modernize_orthography(w)
        # Filtra caracteres no-léxicos restantes dentro de la palabra.
        w = "".join(ch for ch in w if ch in _KEEP_CHARS or ch == "'")
        # Colapsa apóstrofos múltiples consecutivos.
        w = re.sub(r"''+", "'", w)
        w = w.strip("'-")
        if w:
            words_out.append(w)
    return " ".join(words_out)


def _normalize_file(src: Path) -> list[tuple[str, str]]:
    raw = src.read_text(encoding="utf-8")
    # Descarta líneas tipo "«Título»" que aparecen como primera línea del
    # documento antes del primer párrafo real.
    lines = raw.splitlines()
    if lines and lines[0].lstrip().startswith(("«", "\"", "“")):
        lines = lines[1:]
    lines = _merge_broken_speakers(lines)
    lines = _merge_speaker_only_lines(lines)
    paragraphs = _group_paragraphs(lines)

    utterances: list[tuple[str, str]] = []
    current_speaker = "UNK"
    for para in paragraphs:
        items = _split_paragraph_utterances(para)
        if not items:
            continue
        for spk, text in items:
            if spk and not spk.endswith("::quote") and spk != "::quote":
                current_speaker = spk
            effective_speaker = current_speaker
            if spk and spk.endswith("::quote"):
                effective_speaker = f"{current_speaker}::quote"
            clean = _normalize_text(text)
            if clean:
                utterances.append((effective_speaker, clean))
    return utterances


def main() -> int:
    if not SRC_DIR.is_dir():
        print(f"no existe {SRC_DIR}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC_DIR.glob("*.txt"))
    total_lines = 0
    for src in files:
        utts = _normalize_file(src)
        out = OUT_DIR / f"{src.stem}.txt"
        with out.open("w", encoding="utf-8") as fh:
            for idx, (_spk, text) in enumerate(utts):
                print("linea nueva")
                if idx == 0 or idx == len(utts) - 1:
                    fh.write(text)
                else:
                    fh.write(f" {text} ")
                    
        total_lines += len(utts)
        print(f"{src.name}: {len(utts):4d} líneas → {out}")
    print(f"\ntotal: {total_lines} líneas en {len(files)} archivos")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
