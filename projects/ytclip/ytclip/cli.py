from pathlib import Path

from ytclip.download.audio_processor import get_audio_processor
from ytclip.editor.corpus_segment_editor import CorpusSegmentEditor
from ytclip.manifest import SpokenDictionaryManifest
from ytclip.paths import Paths


class YtclipCLI:
    def download(self, paths: Paths, json: Path, force: bool = False):
        spoken_manifest = SpokenDictionaryManifest(json)
        print(f"descargando y recortando en {paths.segments_folder}/ ...")
        counter = 0
        for video in spoken_manifest.videos:
            processor = get_audio_processor(video, paths)
            for segment in video.segments:
                processor.segment_audio(segment, force=force)
                counter += 1
                print(f"[counter: {counter}]")

    def correct(self, paths: Paths):
        source_json = paths.source_segments
        spoken_manifest = SpokenDictionaryManifest(source_json)
        CorpusSegmentEditor(
            videos=spoken_manifest.videos,
            paths=paths,
        ).run()
        spoken_manifest.save_segments_json(source_json)

    def gen_manifest(self, paths: Paths, json: Path, out: Path):
        spoken_manifest = SpokenDictionaryManifest(json)
        spoken_manifest.save_manifest_csv(out)
