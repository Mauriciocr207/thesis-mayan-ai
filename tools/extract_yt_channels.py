"""Extract YouTube channels from corrected_segments_out.json.

Usage:
    python tools/extract_yt_channels.py [path/to/corrected_segments_out.json]
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

YT_HOSTS = ("youtube.com", "youtu.be")


def is_youtube(url: str) -> bool:
    return any(h in url for h in YT_HOSTS)


def fetch_channel(url: str) -> tuple[str, str] | None:
    try:
        out = subprocess.run(
            ["yt-dlp", "--skip-download", "--print", "%(channel)s\t%(channel_url)s", url],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        ).stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"  [error] {url}: {e}", file=sys.stderr)
        return None
    name, _, channel_url = out.partition("\t")
    return name, channel_url


def main(path: Path) -> None:
    entries = json.loads(path.read_text())
    yt_entries = [e for e in entries if is_youtube(e.get("url", ""))]
    print(f"Total entries: {len(entries)} | YouTube entries: {len(yt_entries)}\n")

    by_channel: dict[tuple[str, str], list[str]] = defaultdict(list)
    for i, entry in enumerate(yt_entries, 1):
        url = entry["url"]
        title = entry.get("title", "")
        print(f"[{i}/{len(yt_entries)}] {url}")
        ch = fetch_channel(url)
        if ch is None:
            continue
        by_channel[ch].append(title)

    print("\n=== Canales encontrados ===")
    for (name, channel_url), titles in sorted(by_channel.items(), key=lambda x: -len(x[1])):
        print(f"\n{name}  ({len(titles)} video(s))")
        print(f"  {channel_url}")
        for t in titles:
            print(f"  - {t}")

    out_path = path.with_name("youtube_channels.json")
    out_path.write_text(
        json.dumps(
            [
                {"channel": name, "channel_url": curl, "videos": titles}
                for (name, curl), titles in by_channel.items()
            ],
            ensure_ascii=False,
            indent=2,
        )
    )
    print(f"\nSaved summary → {out_path}")


if __name__ == "__main__":
    default = Path(__file__).resolve().parents[1] / "corpora/annotations/corrected_segments_out.json"
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    main(target)
