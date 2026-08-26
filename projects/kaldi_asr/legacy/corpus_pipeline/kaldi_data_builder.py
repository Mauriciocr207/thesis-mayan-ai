from pathlib import Path
import pandas as pd
import soundfile as sf
from legacy.paths import Paths
from mayanlab.tokenizer import IPA_TO_KALDI, MayaPhonemeTokenizer


class KaldiDataBuilder:
    """Genera los archivos de datos que Kaldi necesita para entrenamiento y alineamiento."""

    def __init__(self, paths: Paths):
        self.paths = paths
        self.tokenizer = MayaPhonemeTokenizer()
        self.recipe_dir = paths.recipe_dir
        self.local_lang_dir = paths.kaldi_local_lang

    def build_data(self, manifest: str, out_dir: str):
        df = pd.read_csv(self.paths.annotations / manifest)
        self._setup_recipe()
        self._build_data_files(df, self.paths.kaldi_data / out_dir)
        self._build_lang_files(df)

    def _setup_recipe(self):
        """Prepara el directorio del recipe como un recipe de Kaldi."""
        self.recipe_dir.mkdir(parents=True, exist_ok=True)
        kaldi_wsj = self.paths.kaldi_root / "egs" / "wsj" / "s5"

        for name in ("steps", "utils"):
            link = self.recipe_dir / name
            if not link.exists():
                link.symlink_to(kaldi_wsj / name)

        path_sh = self.recipe_dir / "path.sh"
        if not path_sh.exists():
            self._write_raw(path_sh, (
                f"export KALDI_ROOT={self.paths.kaldi_root}\n"
                f"[ -f $KALDI_ROOT/tools/env.sh ] && . $KALDI_ROOT/tools/env.sh\n"
                f"export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$PWD:$PATH\n"
                f"[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && "
                f"echo >&2 \"common_path.sh not found\" && exit 1\n"
                f". $KALDI_ROOT/tools/config/common_path.sh\n"
                f"export LC_ALL=C\n"
                f"export PYTHONUNBUFFERED=1"
            ))

        cmd_sh = self.recipe_dir / "cmd.sh"
        if not cmd_sh.exists():
            self._write_raw(cmd_sh, (
                "export train_cmd=run.pl\n"
                "export decode_cmd=run.pl\n"
                "export cuda_cmd=run.pl"
            ))

        conf_dir = self.recipe_dir / "conf"
        conf_dir.mkdir(exist_ok=True)
        mfcc_conf = conf_dir / "mfcc.conf"
        if not mfcc_conf.exists():
            self._write_raw(mfcc_conf, "--use-energy=false\n--sample-frequency=16000")

    def _build_data_files(self, df: pd.DataFrame, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)

        text_lines = []
        seg_lines = []
        wav_lines = []
        utt2spk_lines = []

        for row in df.itertuples():
            utt_id = f"{row.spk_id.strip()}-{row.utt_id}"
            recording_id = row.utt_id

            text_lines.append(f"{utt_id} {row.maya}")

            audio_path = self.paths.segments_folder / f"{recording_id}.wav"
            info = sf.info(str(audio_path))
            duration = info.frames / info.samplerate
            seg_lines.append(f"{utt_id} {recording_id} 0.0 {duration:.2f}")

            wav_lines.append(f"{recording_id} {self.paths.segments_folder}/{recording_id}.wav")

            utt2spk_lines.append(f"{utt_id} {row.spk_id.strip()}")

        self._write_sorted(output_dir / "text", text_lines)
        self._write_sorted(output_dir / "segments", seg_lines)
        self._write_sorted(output_dir / "wav.scp", wav_lines)
        self._write_sorted(output_dir / "utt2spk", utt2spk_lines)

    def _build_lang_files(self, df: pd.DataFrame):
        self.local_lang_dir.mkdir(parents=True, exist_ok=True)

        shared = self.paths.shared_lexicon_dir
        if (shared / "lexicon.txt").exists():
            self._copy_shared_lexicon(shared)
            return

        # Fallback: generar lexicón solo desde este manifest.
        lexicon = {w for words in df["maya"] for w in words.split()}
        lexicon_lines = ["<unk> SPN"]
        for word in sorted(lexicon):
            phonemes = self.tokenizer.tokenize_word(word)
            lexicon_lines.append(f"{word} {' '.join(phonemes)}")

        nonsilence_lines = self.tokenizer.phones
        silence_lines = ["SIL", "SPN"]

        self._write_sorted(self.local_lang_dir / "lexicon.txt", lexicon_lines)
        self._write_sorted(self.local_lang_dir / "nonsilence_phones.txt", nonsilence_lines)
        self._write_sorted(self.local_lang_dir / "silence_phones.txt", silence_lines)
        self._write_raw(self.local_lang_dir / "optional_silence.txt", "SIL")

    def _copy_shared_lexicon(self, shared: Path):
        # Limpia archivos derivados de corridas previas (lexiconp.txt lo genera
        # prepare_lang.sh y puede quedar desincronizado con el lexicón nuevo).
        for stale in ("lexiconp.txt", "lexiconp_silprob.txt", "lexicon_silprob.txt"):
            stale_path = self.local_lang_dir / stale
            if stale_path.exists():
                stale_path.unlink()
        for name in ("lexicon.txt", "nonsilence_phones.txt", "silence_phones.txt", "optional_silence.txt"):
            src = shared / name
            if src.exists():
                (self.local_lang_dir / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    @staticmethod
    def _write_sorted(path: Path, lines: list[str]):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(sorted(lines)) + "\n")

    @staticmethod
    def _write_raw(path: Path, content: str):
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content + "\n")
