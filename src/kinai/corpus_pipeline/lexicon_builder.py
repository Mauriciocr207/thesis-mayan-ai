import re
from pathlib import Path

import pandas as pd

_TEXT_SPLIT = re.compile(r"[\s.,;:!¡?¿()\[\]{}\"«»“”—–…]+")

from kinai.classes.paths import Paths
from kinai.data_collection.tokenizer import (
    IPA_TO_KALDI,
    MayaPhonemeTokenizer,
    modernize_orthography,
    normalize_word,
)


class LexiconBuilder:
    """Genera un lexicón compartido a partir del vocabulario acumulado de
    manifests (todas las iteraciones ≤ target) y, opcionalmente, del texto
    en ``assets/text/``. OOV se descartan (y se reportan)."""

    def __init__(self, paths: Paths, include_lm_text: bool = False):
        self.paths = paths
        self.include_lm_text = include_lm_text
        self.tokenizer = MayaPhonemeTokenizer()

    def build(self) -> dict:
        print("building lexicon files")
        vocab = self._collect_vocab()
        lexicon_entries, oov = self._apply_g2p(vocab)
        self._write(lexicon_entries)
        return {
            "vocab_size": len(vocab),
            "lexicon_size": len(lexicon_entries),
            "oov_count": len(oov),
            "oov_sample": sorted(oov)[:20],
        }

    # ---------- vocab sources ----------
    def _collect_vocab(self) -> set[str]:
        vocab: set[str] = set()
        vocab |= self._vocab_from_manifests()
        if self.include_lm_text:
            vocab |= self._vocab_from_text_assets()
        return vocab

    def _vocab_from_manifests(self) -> set[str]:
        """Vocabulario de todas las iteraciones cuyo id ≤ al actual."""
        target_n = int(self.paths.iter_id.split("_")[1])
        words: set[str] = set()
        iters_root = self.paths.iterations_root
        if not iters_root.exists():
            return words
        for iter_dir in sorted(iters_root.iterdir()):
            if not iter_dir.is_dir() or not iter_dir.name.startswith("iter_"):
                continue
            if int(iter_dir.name.split("_")[1]) > target_n:
                continue
            iter_paths = self._builder.iteration(iter_dir.name)
            for manifest in (iter_paths.data_manifest, iter_paths.align_manifest):
                if manifest.exists():
                    df = pd.read_csv(manifest)
                    for phrase in df["maya"].dropna():
                        for w in phrase.split():
                            n = normalize_word(w)
                            if n:
                                words.add(n)
        return words

    def _vocab_from_text_assets(self) -> set[str]:
        text_dir = self.paths.text_assets_dir
        if not text_dir.exists():
            return set()
        words: set[str] = set()
        for txt in sorted(text_dir.glob("*.txt")):
            content = txt.read_text(encoding="utf-8")
            for token in _TEXT_SPLIT.split(content):
                n = modernize_orthography(normalize_word(token))
                if n:
                    words.add(n)
        return words

    # ---------- g2p ----------
    def _apply_g2p(self, vocab: set[str]) -> tuple[dict[str, list[str]], set[str]]:
        entries: dict[str, list[str]] = {}
        oov: set[str] = set()
        for word in vocab:
            phonemes = self.tokenizer.tokenize(word)
            if phonemes is None:
                oov.add(word)
            else:
                entries[word] = phonemes
        return entries, oov

    # ---------- output ----------
    def _write(self, entries: dict[str, list[str]]):
        out_dir = self.paths.shared_lexicon_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        lexicon_lines = ["<unk> SPN"]
        for word in sorted(entries):
            lexicon_lines.append(f"{word} {''.join(entries[word])}")

        nonsilence = self.tokenizer.phones
        silence = ["SIL", "SPN"]

        self._write_sorted(out_dir / "lexicon.txt", lexicon_lines)
        self._write_sorted(out_dir / "nonsilence_phones.txt", nonsilence)
        self._write_sorted(out_dir / "silence_phones.txt", silence)
        (out_dir / "optional_silence.txt").write_text("SIL\n", encoding="utf-8")

    @staticmethod
    def _write_sorted(path: Path, lines: list[str]):
        path.write_text("\n".join(sorted(lines)) + "\n", encoding="utf-8")


# Re-export helper for external use.
__all__ = ["LexiconBuilder", "_normalize_iter_id"]
