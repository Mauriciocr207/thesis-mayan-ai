from pathlib import Path

from kinai.classes.paths import Paths
from kinai.corpus_pipeline.kaldi_aligner import KaldiAligner
from kinai.corpus_pipeline.kaldi_data_builder import KaldiDataBuilder
from kinai.corpus_pipeline.kaldi_long_segmenter import KaldiLongSegmenter
from kinai.corpus_pipeline.kaldi_trainer import KaldiTrainer
from kinai.corpus_pipeline.lexicon_builder import LexiconBuilder
from kinai.corpus_pipeline.lm_builder import LMBuilder
from kinai.data_collection.audio_processor import get_audio_processor
from kinai.data_collection.corpus_segment_editor import CorpusSegmentEditor
from kinai.data_collection.spoken_dictionary_manifest import SpokenDictionaryManifest


class KinaiCLI:
    def download(self, paths: Paths, json: Path, force):
        spoken_manifest = SpokenDictionaryManifest(json)
        print("check assets/segmented_audio/ - downloading audio files...")
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

    def gen_data(self, paths:Paths, manifest: Path, out_dir: str):
        builder = KaldiDataBuilder(paths)
        builder.build_data(manifest, out_dir)

    def gen_manifest(self, paths: Paths, json: str, out: str):
        spoken_manifest = SpokenDictionaryManifest(paths.annotations / json)
        spoken_manifest.save_manifest_csv(paths.annotations / out)

    def train(self, paths: Paths, experiment: str, nj: int = 1):
        spoken_manifest = SpokenDictionaryManifest(paths.source_segments)
        spoken_manifest.save_manifest_csv(paths.data_manifest)
        builder = KaldiDataBuilder(paths)
        builder.build_train_data()
        trainer = KaldiTrainer(paths, experiment, nj)
        trainer.train()

    def align(self, paths: Paths, model_path: Path, nj: int = 1):
        aligner = KaldiAligner(paths, model_path, nj)
        aligner.align()

    def segment(self, paths: Paths, model_path: Path, lang_path: Path, nj: int = 1):
        segmenter = KaldiLongSegmenter(paths, model_path, lang_path, nj)
        segmenter.segment()

    def build_lm(self, paths: Paths, kind: str, order: int = 3, transcripts_weight: int = 3):
        LMBuilder(paths, kind=kind, order=order, transcripts_weight=transcripts_weight).build()

    def gen_lexicon(self, paths: Paths, include_lm_text: bool = False):
        stats = LexiconBuilder(paths, include_lm_text=include_lm_text).build()
        print(
            f"[lexicon] vocab={stats['vocab_size']} "
            f"lexicon={stats['lexicon_size']} oov={stats['oov_count']}"
        )
        if stats["oov_sample"]:
            print(f"[lexicon] OOV sample: {stats['oov_sample']}")
