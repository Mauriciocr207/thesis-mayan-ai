from pathlib import Path
import subprocess
import numpy as np
import soundfile as sf
from ytclip.paths import Paths
from ytclip.models.video_annotation import Segment, VideoAnnotation


class AudioProcessor:
    """Base: segmenta un archivo de audio según los Segments del VideoAnnotation."""

    def __init__(self, video: VideoAnnotation, paths: Paths):
        self.video = video
        self.paths = paths
        self.out_seg_dir = paths.segments_folder
        self.out_seg_dir.mkdir(parents=True, exist_ok=True)
        self.video_path: Path | None = None

    def _prepare_source(self):
        """Sobrescribir: debe dejar self.video_path apuntando al audio fuente."""
        raise NotImplementedError

    def segment_audio(self, segment: Segment, force=False):
        audio_path = self.out_seg_dir / f"{segment.utt_id}.wav"
        if audio_path.exists() and not force:
            print(f"[skip] {segment.utt_id} (already exists)")
            return

        self._prepare_source()
        print(f"[segmenting] {segment.utt_id} ({segment.start} → {segment.end})")

        subprocess.run([
            "ffmpeg",
            "-loglevel", "error",
            "-y",
            "-i", str(self.video_path),
            "-ss", segment.start,
            "-to", segment.end,
            "-ac", "1",
            "-ar", "16000",
            str(audio_path)
        ], check=True)

        self._normalize_peak(audio_path)
        print(f"[done] {segment.utt_id}")

    @staticmethod
    def _normalize_peak(path: Path, target: float = 0.99):
        data, sr = sf.read(path)
        peak = np.max(np.abs(data))
        if peak > 0:
            data = data * (target / peak)
        sf.write(path, data, sr, subtype="PCM_16")


class YouTubeAudioProcessor(AudioProcessor):
    def __init__(self, video: VideoAnnotation, paths: Paths):
        super().__init__(video, paths)
        self.tmp_dir = paths.yt_audio_folder
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        safe_title = "".join(c for c in video.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        self.yt_dlp_output = self.tmp_dir / f"{safe_title}.%(ext)s"
        self.video_path = self.tmp_dir / f"{safe_title}.wav"

    def _ydl_opts(self) -> list:
        return [
            "yt-dlp",
            "-f", "bestaudio/best",
            "-o", str(self.yt_dlp_output),
            "--postprocessor-args", "ffmpeg:-acodec pcm_s16le -ar 16000 -ac 1",
            "-x", "--audio-format", "wav",
            "--extractor-args", "youtube:player-client=web_embedded,web,tv",
            "--cookies-from-browser", "firefox",
            "--js-runtimes", "node",
            "--remote-components", "ejs:github",
            self.video.url,
        ]

    def _prepare_source(self):
        if self.video_path.exists():
            return
        subprocess.run(self._ydl_opts(), check=True)


class LocalAudioProcessor(AudioProcessor):
    """Usa un archivo local cuya ruta está en video.url (relativa al root del proyecto)."""

    def __init__(self, video: VideoAnnotation, paths: Paths):
        super().__init__(video, paths)
        self.video_path = paths.root / video.url

    def _prepare_source(self):
        if not self.video_path.exists():
            raise FileNotFoundError(f"Local source audio not found: {self.video_path}")


def get_audio_processor(video: VideoAnnotation, paths: Paths) -> AudioProcessor:
    """Devuelve el processor apropiado según el formato del url."""
    if video.url.startswith("http"):
        return YouTubeAudioProcessor(video, paths)
    return LocalAudioProcessor(video, paths)
