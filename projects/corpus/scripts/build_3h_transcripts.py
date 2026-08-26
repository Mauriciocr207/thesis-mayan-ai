#!/usr/bin/env python
"""Completa y valida las transcripciones alineadas del subcorpus de 3 h (INALI).

Contexto
--------
El texto del subcorpus de narraciones (1.227 utterances, hablantes 01–15) venía
de dos sitios distintos, y eso dejaba `data/final/transcripts/` incompleto:

* hablantes 04–15 → un `.txt` por narración, un bloque por utterance;
* hablantes 01–03 → la columna `correction` de
  `data/source/annotations/3h-corrected-transcripts-manual.csv`, sin `.txt`.

Este script materializa los tres `.txt` que faltaban con el mismo formato que
los doce existentes, de modo que `data/final/transcripts/` sea la fuente única
y uniforme del texto del 3 h.

Formato de los `.txt`
---------------------
Un bloque por utterance separado por línea en blanco (`"utt\\n\\nutt\\n\\n…"`),
sin salto de línea final, en el orden de los segmentos. Un bloque puede contener
saltos de línea internos (ocurre en el bloque 142 de `15_Mario_Chan.txt`); por
eso el corte es por `\\n\\n` y no por `\\n`.

Uso
---
    python build_3h_transcripts.py            # genera lo que falte y valida
    python build_3h_transcripts.py --check    # solo valida, no escribe
"""

from __future__ import annotations

import argparse
import sys
import unicodedata

import pandas as pd

from mayanlab.paths import ANNOTATIONS, MANIFESTS, TRANSCRIPTS, ensure

# Hablantes cuyo texto alineado solo existía en la columna `correction` del CSV.
FROM_CSV = ("01_Anatolio_Pech", "02_Liboria_May", "03_Eligio_Uicab_Jatswooj")

CORRECTED_CSV = ANNOTATIONS / "3h-corrected-transcripts-manual.csv"
SEGMENTS_CSV = ANNOTATIONS / "3h-transcripts.csv"
DATASET_CSV = MANIFESTS / "dataset.csv"


def normalize(text: object) -> str:
    """Normalización mínima para comparar: NFC, espacios colapsados."""
    return " ".join(unicodedata.normalize("NFC", str(text)).split())


def read_blocks(path) -> list[str]:
    """Lee un .txt de transcripciones y devuelve un bloque por utterance."""
    return path.read_text(encoding="utf-8").split("\n\n")


def write_blocks(path, blocks: list[str]) -> None:
    path.write_text("\n\n".join(blocks), encoding="utf-8")


def build(check_only: bool) -> list[str]:
    """Genera los .txt que falten. Devuelve la lista de archivos escritos."""
    corrected = pd.read_csv(CORRECTED_CSV)
    written: list[str] = []

    for name in FROM_CSV:
        target = TRANSCRIPTS / f"{name}.txt"
        rows = corrected.loc[corrected["file_name"] == name, "correction"]

        if rows.empty:
            sys.exit(f"[error] {name} no aparece en {CORRECTED_CSV.name}")
        if rows.isna().any():
            sys.exit(f"[error] {name} tiene {int(rows.isna().sum())} correcciones vacías")

        blocks = [str(x).strip() for x in rows]
        if any("\n\n" in b for b in blocks):
            sys.exit(f"[error] {name}: una corrección contiene una línea en blanco, "
                     "rompería el formato de bloques")

        if target.exists() and read_blocks(target) == blocks:
            print(f"[ok]    {name}.txt ya está al día ({len(blocks)} bloques)")
            continue
        if check_only:
            print(f"[falta] {name}.txt ({len(blocks)} bloques) — ejecuta sin --check")
            continue

        ensure(TRANSCRIPTS)
        write_blocks(target, blocks)
        written.append(target.name)
        print(f"[nuevo] {name}.txt ({len(blocks)} bloques)")

    return written


def validate() -> None:
    """Comprueba que los .txt reproducen exactamente el dataset publicado."""
    segments = pd.read_csv(SEGMENTS_CSV)
    expected_counts = segments["audio_file"].value_counts().to_dict()

    dataset = pd.read_csv(DATASET_CSV)
    three_h = dataset[dataset["filename"].str.match(r"^\d\d_.+_\d+$", na=False)].copy()
    three_h["file_name"] = three_h["filename"].str.replace(r"_\d+$", "", regex=True)
    three_h["idx"] = three_h["filename"].str.extract(r"_(\d+)$").astype(int)

    problems: list[str] = []
    total = 0

    for name, expected in sorted(expected_counts.items()):
        path = TRANSCRIPTS / f"{name}.txt"
        if not path.exists():
            problems.append(f"{name}: falta {path.name}")
            continue

        blocks = read_blocks(path)
        total += len(blocks)
        if len(blocks) != expected:
            problems.append(f"{name}: {len(blocks)} bloques, se esperaban {expected}")
            continue

        published = three_h[three_h["file_name"] == name].sort_values("idx")["maya"]
        mismatches = [
            i for i, (block, maya) in enumerate(zip(blocks, published), start=1)
            if normalize(block) != normalize(maya)
        ]
        if mismatches:
            problems.append(
                f"{name}: {len(mismatches)} bloques distintos de dataset.csv "
                f"(primero: utterance {mismatches[0]})"
            )
        else:
            print(f"[ok]    {name:<28} {len(blocks):>4} utterances == dataset.csv")

    if total != len(three_h):
        problems.append(f"total {total} bloques != {len(three_h)} filas del 3h en dataset.csv")

    if problems:
        print("\n[FALLO] la validación encontró problemas:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)

    print(f"\n[OK] {len(expected_counts)} archivos, {total} utterances, "
          f"coincidencia exacta con la columna maya de dataset.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="solo valida, no escribe nada")
    args = parser.parse_args()

    build(check_only=args.check)
    print()
    validate()


if __name__ == "__main__":
    main()
