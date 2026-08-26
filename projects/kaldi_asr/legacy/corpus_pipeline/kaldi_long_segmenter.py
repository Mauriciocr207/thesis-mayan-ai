import json
import subprocess
from datetime import timedelta
from pathlib import Path

import soundfile as sf

from legacy.paths import Paths
from legacy.corpus_pipeline.kaldi_data_builder import KaldiDataBuilder
from ytclip.download.audio_processor import get_audio_processor
from ytclip.manifest import SpokenDictionaryManifest
from ytclip.models.video_annotation import VideoAnnotation


class KaldiLongSegmenter(KaldiDataBuilder):
    """Segmenta audios largos usando steps/cleanup/segment_long_utterances.sh.

    Entrada: `long_sources.json` con el schema de VideoAnnotation, donde cada
    video es UNA grabación completa (10–20 min) y sus `segments[*].maya`
    concatenados forman el transcript completo. Los tiempos se ignoran.

    Flujo:
      1. Resuelve audio fuente de cada video (YouTube → descarga; local → valida).
      2. Construye `kaldi/data/long/` apuntando al audio fuente completo:
         wav.scp (una línea por recording), segments (0.0 → duración real),
         text (transcript completo), utt2spk.
      3. Extrae MFCC.
      4. Invoca segment_long_utterances.sh con el modelo + lang.
      5. Convierte `data/long_reseg/{segments,text}` a `source_segments.json`.
    """

    LONG_DIR = "long"
    RESEG_DIR = "long_reseg"
    WORK_DIR_NAME = "segment_long_work"

    def __init__(self, paths: Paths, model_path: Path, lang_path: Path, nj: int = 1):
        self.paths = paths
        self.recipe_dir = paths.recipe_dir
        self.model_path = model_path
        self.lang_path = lang_path
        self.nj = nj
        super().__init__(paths)

    def segment(self):
        sources_file = self.paths.long_sources
        if not sources_file.exists():
            raise RuntimeError(f"long_sources.json not found: {sources_file}")
        if not self.model_path.exists():
            raise RuntimeError(f"Model not found: {self.model_path}")
        if not self.lang_path.exists():
            raise RuntimeError(f"Lang dir not found: {self.lang_path}")

        manifest = SpokenDictionaryManifest(sources_file)
        videos = manifest.videos

        audio_paths = self._resolve_audio(videos)
        self._setup_recipe()
        self._write_long_data_dir(videos, audio_paths)
        self._extract_features()
        self._run_segmentation()
        self._write_source_segments(videos)

    # ---------- IO ----------
    def _resolve_audio(self, videos: list[VideoAnnotation]) -> dict[str, Path]:
        """Descarga/valida el audio fuente de cada video → rec_id → path."""
        out: dict[str, Path] = {}
        for video in videos:
            processor = get_audio_processor(video, self.paths)
            processor._prepare_source()
            if processor.video_path is None or not processor.video_path.exists():
                raise RuntimeError(f"Audio not resolved for {video.url}")
            out[VideoAnnotation._get_url_id(video.url)] = processor.video_path.resolve()
        return out

    def _write_long_data_dir(
        self,
        videos: list[VideoAnnotation],
        audio_paths: dict[str, Path],
    ):
        out_dir = self.paths.kaldi_data / self.LONG_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        wav_lines: list[str] = []
        seg_lines: list[str] = []
        text_lines: list[str] = []
        utt2spk_lines: list[str] = []

        for video in videos:
            url_id = VideoAnnotation._get_url_id(video.url)
            src = audio_paths[url_id]
            info = sf.info(str(src))
            duration = info.frames / info.samplerate

            spk = (video.segments[0].spk_id if video.segments else None) or "unk"
            utt = f"{spk}-{url_id}"
            transcript = " ".join(s.maya.strip() for s in video.segments if s.maya).strip()
            if not transcript:
                raise RuntimeError(f"Empty transcript for {video.url}")

            wav_lines.append(f"{url_id} {src}")
            seg_lines.append(f"{utt} {url_id} 0.0 {duration:.2f}")
            text_lines.append(f"{utt} {transcript}")
            utt2spk_lines.append(f"{utt} {spk}")

        self._write_sorted(out_dir / "wav.scp", wav_lines)
        self._write_sorted(out_dir / "segments", seg_lines)
        self._write_sorted(out_dir / "text", text_lines)
        self._write_sorted(out_dir / "utt2spk", utt2spk_lines)
        self._run(f"utils/utt2spk_to_spk2utt.pl data/{self.LONG_DIR}/utt2spk > data/{self.LONG_DIR}/spk2utt")
        self._run(f"utils/fix_data_dir.sh data/{self.LONG_DIR}")

    def _extract_features(self):
        self._run(f"steps/make_mfcc.sh --nj {self.nj} --cmd run.pl data/{self.LONG_DIR}")
        self._run(f"steps/compute_cmvn_stats.sh data/{self.LONG_DIR}")
        self._run(f"utils/fix_data_dir.sh data/{self.LONG_DIR}")

    def _run_segmentation(self):
        work_dir = f"exp/{self.WORK_DIR_NAME}"
        self._run(
            f"steps/cleanup/segment_long_utterances.sh --nj {self.nj} --cmd run.pl "
            f"{self.model_path} {self.lang_path} "
            f"data/{self.LONG_DIR} data/{self.RESEG_DIR} {work_dir}"
        )

    def _write_source_segments(self, videos: list[VideoAnnotation]):
        reseg_dir = self.recipe_dir / "data" / self.RESEG_DIR
        segments_file = reseg_dir / "segments"
        text_file = reseg_dir / "text"
        if not segments_file.exists() or not text_file.exists():
            raise RuntimeError(f"Expected output missing in {reseg_dir}")

        seg_map: dict[str, tuple[str, float, float]] = {}
        for line in segments_file.read_text(encoding="utf-8").splitlines():
            sub_utt, rec, start, end = line.split()
            seg_map[sub_utt] = (rec, float(start), float(end))

        text_map: dict[str, str] = {}
        for line in text_file.read_text(encoding="utf-8").splitlines():
            sub_utt, _, maya = line.partition(" ")
            text_map[sub_utt] = maya

        # Cada recording en el output del segmenter corresponde a un url_id
        # (la grabación completa fue introducida como una sola utterance).
        url_to_spk: dict[str, str] = {}
        for v in videos:
            url_id = VideoAnnotation._get_url_id(v.url)
            spk = (v.segments[0].spk_id if v.segments else None) or "unk"
            url_to_spk[url_id] = spk

        by_url: dict[str, list[dict]] = {
            VideoAnnotation._get_url_id(v.url): [] for v in videos
        }
        for sub_utt, (rec, sub_start, sub_end) in seg_map.items():
            spk = url_to_spk.get(rec)
            if spk is None:
                print(f"[segment_long] warning: recording sin origen: {rec}")
                continue
            maya = self._clean_text(text_map.get(sub_utt, ""))
            if not maya:
                continue  # sub-segmento puro <unk>/silencio; descartar
            by_url[rec].append({
                "maya": maya,
                "spanish": "",
                "start": _sec_to_hms(sub_start),
                "end": _sec_to_hms(sub_end),
                "spk_id": spk,
            })

        for url_id in by_url:
            by_url[url_id].sort(key=lambda s: s["start"])

        output = []
        for video in videos:
            url_id = VideoAnnotation._get_url_id(video.url)
            output.append({
                "url": video.url,
                "title": video.title,
                "segments": by_url.get(url_id, []),
                "metadata": video.metadata or {},
            })

        out_file = self.paths.source_segments
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[segment_long] wrote {out_file}")

    # ---------- helpers ----------
    @staticmethod
    def _clean_text(text: str) -> str:
        """Quita tokens <unk> que segment_long inserta para padding/ruido."""
        return " ".join(w for w in text.split() if w != "<unk>").strip()

    def _run(self, cmd: str):
        full_cmd = f". ./path.sh && . ./cmd.sh && {cmd}"
        print(f"[kaldi] {cmd}")
        result = subprocess.run(
            full_cmd, shell=True, cwd=self.recipe_dir, capture_output=True, text=True,
        )
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            raise RuntimeError(f"Kaldi failed: {cmd}")

    @staticmethod
    def _write_sorted(path: Path, lines: list[str]):
        path.write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")


def _sec_to_hms(seconds: float) -> str:
    td = timedelta(seconds=seconds)
    total_ms = int(td.total_seconds() * 1000)
    h = total_ms // 3_600_000
    total_ms %= 3_600_000
    m = total_ms // 60_000
    total_ms %= 60_000
    s = total_ms // 1000
    ms = total_ms % 1000
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"
