from enum import Enum


class Dirs(str, Enum):
    assets = "assets"
    yt_audio = "sources/yt_audio"
    segmented_audio = "segmented_audio"
    ann = "annotations"
    kaldi = "kaldi"
    corpora = "corpora"
    iterations = "iterations"
    shared = "shared"
    lexicon = "lexicon"
    text = "text"


class Files(str, Enum):
    source = "source_segments.json"
    ali_man = "align_manifest.csv"
    data_man = "data_manifest.csv"
    long_srcs = "long_sources.json"
