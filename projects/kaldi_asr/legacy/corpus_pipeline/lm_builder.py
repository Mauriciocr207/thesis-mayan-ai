import gzip
import math
import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterator

import pandas as pd

from legacy.paths import Paths
from mayanlab.tokenizer import modernize_orthography, normalize_word

_TEXT_SPLIT = re.compile(r"[\s.,;:!¡?¿()\[\]{}\"«»“”—–…]+")


class LMBuilder:
    """Construye un language model (flat o n-gram con KenLM) y lo compila a G.fst.

    - ``flat``: ARPA unigrama uniforme (1/|V|). No requiere binarios externos.
    - ``ngram``: entrena con ``lmplz`` de KenLM sobre texto concat ponderado
      (transcripciones × peso + biblia modernizada y filtrada contra el lexicón).
    """

    def __init__(
        self,
        paths: Paths,
        kind: str = "flat",
        order: int = 3,
        transcripts_weight: int = 3,
    ):
        if kind not in {"flat", "ngram"}:
            raise ValueError(f"kind debe ser 'flat' o 'ngram', no '{kind}'")
        self.paths = paths
        self.kind = kind
        self.order = order
        self.transcripts_weight = transcripts_weight

    # ---------- entrypoint ----------
    def build(self) -> Path:
        lm_work = self.paths.recipe_dir / "data" / "local" / "lm"
        lm_work.mkdir(parents=True, exist_ok=True)

        arpa = lm_work / f"lm_{self.kind}.arpa"
        if self.kind == "flat":
            self._build_flat(arpa)
        else:
            self._build_ngram(arpa, lm_work)

        arpa_gz = arpa.with_suffix(".arpa.gz")
        with open(arpa, "rb") as f_in, gzip.open(arpa_gz, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

        lang_test = self._compile_to_fst(arpa_gz)
        print(f"[lm] {self.kind} ready: {arpa_gz} -> {lang_test}")
        return lang_test

    # ---------- flat ----------
    def _build_flat(self, out_arpa: Path):
        lex_words = self._read_lexicon_words()
        # <s>/</s> son tokens de frontera obligatorios en ARPA
        words = sorted(lex_words)
        n = len(words) + 1  # +1 por </s>; <s> recibe -99 por convención
        logp = math.log10(1.0 / n)

        lines = ["", "\\data\\", f"ngram 1={n + 1}", "", "\\1-grams:"]
        lines.append(f"-99\t<s>")
        lines.append(f"{logp:.6f}\t</s>")
        for w in words:
            lines.append(f"{logp:.6f}\t{w}")
        lines.append("")
        lines.append("\\end\\")
        out_arpa.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[lm:flat] |V|={n} uniform_logp={logp:.4f}")

    # ---------- ngram (KenLM) ----------
    def _build_ngram(self, out_arpa: Path, work_dir: Path):
        lmplz = shutil.which("lmplz")
        if not lmplz:
            raise RuntimeError(
                "lmplz no encontrado en PATH. Instala KenLM con tools/install_kenlm.sh "
                "y añade tools/kenlm/build/bin al PATH."
            )

        corpus_file = work_dir / "train_text.txt"
        self._write_training_corpus(corpus_file)

        cmd = [lmplz, "-o", str(self.order), "--discount_fallback", "--text", str(corpus_file), "--arpa", str(out_arpa)]
        print(f"[lm:ngram] {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

    def _write_training_corpus(self, out: Path):
        vocab = self._read_lexicon_words()
        lines: list[str] = []

        # (a) transcripciones, repetidas para peso
        transcripts = list(self._transcript_lines())
        for _ in range(max(1, self.transcripts_weight)):
            lines.extend(transcripts)

        # (b) texto externo, modernizado y filtrado contra lexicón
        for line in self._external_text_lines():
            clean = [w for w in line.split() if w in vocab]
            if clean:
                lines.append(" ".join(clean))

        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"[lm:ngram] corpus: {len(lines)} lines -> {out}")

    def _transcript_lines(self) -> Iterator[str]:
        target_n = int(self.paths.iter_id.split("_")[1])
        for iter_dir in sorted(self.paths.iterations_root.iterdir()):
            if not iter_dir.is_dir() or not iter_dir.name.startswith("iter_"):
                continue
            if int(iter_dir.name.split("_")[1]) > target_n:
                continue
            iter_paths = self._builder.iteration(iter_dir.name)
            for manifest in (iter_paths.data_manifest, iter_paths.align_manifest):
                if not manifest.exists():
                    continue
                df = pd.read_csv(manifest)
                for phrase in df["maya"].dropna():
                    words = [normalize_word(w) for w in phrase.split()]
                    words = [w for w in words if w]
                    if words:
                        yield " ".join(words)

    def _external_text_lines(self) -> Iterator[str]:
        text_dir = self.paths.text_assets_dir
        if not text_dir.exists():
            return
        for txt in sorted(text_dir.glob("*.txt")):
            for raw_line in txt.read_text(encoding="utf-8").splitlines():
                tokens = [
                    modernize_orthography(normalize_word(t))
                    for t in _TEXT_SPLIT.split(raw_line)
                ]
                tokens = [t for t in tokens if t]
                if tokens:
                    yield " ".join(tokens)

    # ---------- fst ----------
    def _compile_to_fst(self, arpa: Path) -> Path:
        lang_dir = self.paths.kaldi_data / "lang"
        if not lang_dir.exists():
            raise RuntimeError(
                f"{lang_dir} no existe. Corre primero `kinai gen-train-data` "
                "(o gen-align-data) para preparar data/lang."
            )

        lexicon = self.paths.kaldi_local_lang / "lexicon.txt"
        lang_test = self.paths.kaldi_data / f"lang_test_{self.kind}"
        if lang_test.exists():
            shutil.rmtree(lang_test)

        self._run_in_recipe(
            f"utils/format_lm.sh {lang_dir.relative_to(self.paths.recipe_dir)} "
            f"{arpa.relative_to(self.paths.recipe_dir)} "
            f"{lexicon.relative_to(self.paths.recipe_dir)} "
            f"{lang_test.relative_to(self.paths.recipe_dir)}"
        )
        return lang_test

    # ---------- helpers ----------
    def _read_lexicon_words(self) -> set[str]:
        lex_path = self.paths.shared_lexicon_dir / "lexicon.txt"
        if not lex_path.exists():
            raise RuntimeError(
                f"Lexicón compartido no existe: {lex_path}. Corre `kinai gen-lexicon` primero."
            )
        words: set[str] = set()
        for line in lex_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            word = line.split()[0]
            if word != "<unk>":
                words.add(word)
        return words

    def _run_in_recipe(self, cmd: str):
        full_cmd = f". ./path.sh && . ./cmd.sh && {cmd}"
        print(f"[kaldi] {cmd}")
        result = subprocess.run(
            full_cmd, shell=True, cwd=self.paths.recipe_dir, capture_output=True, text=True,
        )
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            raise RuntimeError(f"Kaldi failed: {cmd}")
