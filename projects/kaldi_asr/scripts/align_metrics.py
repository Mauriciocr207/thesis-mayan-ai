"""Resume métricas del alignment de Kaldi (steps/align_si.sh).

Uso:
    python projects/kaldi_asr/scripts/align_metrics.py <iter_id>
    python projects/kaldi_asr/scripts/align_metrics.py 02
    python projects/kaldi_asr/scripts/align_metrics.py <ruta a exp/ali>
"""
import re
import sys
from pathlib import Path

RECIPE = Path(__file__).resolve().parents[1] / "recipe"


def resolve_ali_dir(arg: str) -> Path:
    p = Path(arg)
    if p.is_dir():
        return p
    iter_id = arg if arg.startswith("iter_") else f"iter_{int(arg):02d}"
    return RECIPE / "iterations" / iter_id / "exp" / "ali"


def parse_align_logs(ali_dir: Path):
    done = err = frames = 0
    weighted_prob = 0.0
    failed_utts: list[str] = []
    for log in sorted((ali_dir / "log").glob("align.*.log")):
        text = log.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"Done (\d+), errors on (\d+)", text):
            done += int(m.group(1))
            err += int(m.group(2))
        for m in re.finditer(
            r"Overall log-likelihood per frame is (-?[\d.]+) over (\d+) frames", text
        ):
            prob, n = float(m.group(1)), int(m.group(2))
            weighted_prob += prob * n
            frames += n
        for m in re.finditer(r"Did not successfully decode file (\S+?),? len", text):
            failed_utts.append(m.group(1))
    avg_prob = weighted_prob / frames if frames else float("nan")
    return done, err, frames, avg_prob, failed_utts


def parse_analyze_log(ali_dir: Path):
    log = ali_dir / "log" / "analyze_alignments.log"
    if not log.exists():
        return {}
    text = log.read_text(encoding="utf-8", errors="replace")
    out = {}
    m = re.search(r"optional-silence phone SIL occupies ([\d.]+)% of frames", text)
    if m:
        out["sil_pct_overall"] = float(m.group(1))
    m = re.search(
        r"Limiting the stats to the ([\d.]+)% of frames not covered by an "
        r"utterance-\[begin/end\] phone, optional-silence SIL occupies ([\d.]+)%",
        text,
    )
    if m:
        out["non_boundary_frames_pct"] = float(m.group(1))
        out["sil_pct_non_boundary"] = float(m.group(2))
    m = re.search(
        r"Utterance-internal optional-silences SIL comprise ([\d.]+)%", text
    )
    if m:
        out["sil_pct_internal"] = float(m.group(1))
    m = re.search(r"alignments represent ([\d.]+) hours", text)
    if m:
        out["hours"] = float(m.group(1))
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    ali_dir = resolve_ali_dir(sys.argv[1])
    if not ali_dir.exists():
        print(f"ali dir not found: {ali_dir}")
        sys.exit(1)

    done, err, frames, avg_prob, failed = parse_align_logs(ali_dir)
    total = done + err
    analyze = parse_analyze_log(ali_dir)

    print(f"=== {ali_dir} ===")
    print(f"Alineadas:     {done}/{total} ({done / total * 100:.1f}%)" if total else "Alineadas: 0/0")
    print(f"Errores:       {err}/{total} ({err / total * 100:.1f}%)" if total else "")
    print(f"Frames:        {frames} ({frames / 100 / 60:.1f} min @ 100fps)")
    print(f"Log-prob/frame: {avg_prob:.2f}")
    if analyze:
        print(f"SIL % (total):        {analyze.get('sil_pct_overall', 'n/a')}%")
        print(f"SIL % (non-boundary): {analyze.get('sil_pct_non_boundary', 'n/a')}%")
        print(f"SIL % (internal):     {analyze.get('sil_pct_internal', 'n/a')}%")
        print(f"Hours aligned:        {analyze.get('hours', 'n/a')}")
    if failed:
        sample = ", ".join(failed[:5])
        suffix = "" if len(failed) <= 5 else f" (+{len(failed) - 5} más)"
        print(f"Fallos (muestra): {sample}{suffix}")


if __name__ == "__main__":
    main()
