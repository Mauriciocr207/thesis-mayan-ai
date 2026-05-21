"""Añade padding en segundos a los segmentos de un source_segments.json.

Uso:
    python tools/pad_segments.py <path> [pad_sec]

Escribe un `.bak` junto al archivo original antes de reescribir.
"""
import json
import sys
from pathlib import Path
from kinai.utils.format_json import format_json


def _parse_hms(ts: str) -> float:
    h, m, rest = ts.split(":")
    s, ms = rest.split(".") if "." in rest else (rest, "0")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms.ljust(3, "0")[:3]) / 1000


def _to_hms(sec: float) -> str:
    total_ms = max(0, int(round(sec * 1000)))
    h, total_ms = divmod(total_ms, 3_600_000)
    m, total_ms = divmod(total_ms, 60_000)
    s, ms = divmod(total_ms, 1000)
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "corpora/annotations/source_segments.json"
    )
    pad = float(sys.argv[2]) if len(sys.argv) > 2 else 0.15

    data = json.loads(path.read_text(encoding="utf-8"))
    path.with_suffix(path.suffix + ".bak").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    n = 0
    for video in data:
        for seg in video.get("segments", []):
            start = max(0.0, _parse_hms(seg["start"]) - pad)
            end = _parse_hms(seg["end"]) + pad
            seg["start"] = _to_hms(start)
            seg["end"] = _to_hms(end)
            n += 1

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    format_json(path)
    print(f"{n} segmentos con ±{pad}s de padding → {path}")


if __name__ == "__main__":
    main()
