import json
import subprocess
from pathlib import Path

from kinai.classes.paths import Paths
from kinai.corpus_pipeline.kaldi_data_builder import KaldiDataBuilder
from kinai.data_collection.spoken_dictionary_manifest import SpokenDictionaryManifest


class KaldiAligner:
    """Forced alignment de utterances cortas + export de CTM palabra-nivel.

    Flujo end-to-end:
      1. Genera align_manifest.csv desde source_segments.json.
      2. Construye kaldi/data/align/ (wav.scp, segments, text, utt2spk)
         y kaldi/data/local/lang/.
      3. Extrae MFCC y CMVN.
      4. Ejecuta `steps/align_si.sh` usando el modelo externo.
      5. Ejecuta `steps/get_train_ctm.sh` sobre el alignment dir.
      6. Copia el CTM a annotations/word_alignments.ctm y genera un JSON
         estructurado (annotations/word_alignments.json) para consumo
         desde notebooks.
    """

    ALIGN_DIR = "align"
    EXP_ALI = "exp/ali"

    def __init__(self, paths: Paths, model_path: Path, nj: int = 1):
        self.paths = paths
        self.recipe_dir = paths.recipe_dir
        self.model_path = model_path
        self.nj = nj

    def align(self):
        if not self.model_path.exists():
            raise RuntimeError(f"Model not found: {self.model_path}")

        self._build_manifest_and_data()
        self._prepare_lang()
        self._prepare_data()
        self._extract_features()
        self._align()
        self._get_ctm()
        self._export_word_alignments()

    # ---------- steps ----------
    def _build_manifest_and_data(self):
        spoken = SpokenDictionaryManifest(self.paths.source_segments)
        spoken.save_manifest_csv(self.paths.align_manifest)
        builder = KaldiDataBuilder(self.paths)
        builder.build_align_data()

    def _prepare_lang(self):
        self._run(
            'utils/prepare_lang.sh data/local/lang "<unk>" data/local/lang_tmp data/lang'
        )

    def _prepare_data(self):
        self._run(f"utils/fix_data_dir.sh data/{self.ALIGN_DIR}")
        self._run(f"utils/validate_data_dir.sh data/{self.ALIGN_DIR} --no-feats", warn_only=True)

    def _extract_features(self):
        self._run(f"steps/make_mfcc.sh --nj {self.nj} --cmd run.pl data/{self.ALIGN_DIR}")
        self._run(f"steps/compute_cmvn_stats.sh data/{self.ALIGN_DIR}")
        self._run(f"utils/fix_data_dir.sh data/{self.ALIGN_DIR}")
        self._run(f"utils/validate_data_dir.sh data/{self.ALIGN_DIR}", warn_only=True)

    def _align(self):
        self._run(
            f"steps/align_si.sh --nj {self.nj} --cmd run.pl "
            f"data/{self.ALIGN_DIR} data/lang {self.model_path} {self.EXP_ALI}"
        )

    def _get_ctm(self):
        self._run(
            f"steps/get_train_ctm.sh --cmd run.pl --use-segments true "
            f"data/{self.ALIGN_DIR} data/lang {self.EXP_ALI}"
        )

    def _export_word_alignments(self):
        ctm_src = self.recipe_dir / self.EXP_ALI / "ctm"
        if not ctm_src.exists():
            raise RuntimeError(f"CTM not generated: {ctm_src}")

        annotations = self.paths.annotations
        annotations.mkdir(parents=True, exist_ok=True)

        ctm_dst = annotations / "word_alignments.ctm"
        ctm_dst.write_text(ctm_src.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[align] wrote {ctm_dst}")

        by_utt: dict[str, list[dict]] = {}
        for line in ctm_src.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue
            utt, _ch, start, dur, word = parts[:5]
            start_f, dur_f = float(start), float(dur)
            by_utt.setdefault(utt, []).append({
                "word": word,
                "start": round(start_f, 3),
                "end": round(start_f + dur_f, 3),
            })

        for utt in by_utt:
            by_utt[utt].sort(key=lambda w: w["start"])

        payload = [{"utt_id": utt, "words": by_utt[utt]} for utt in sorted(by_utt)]
        json_dst = annotations / "word_alignments.json"
        json_dst.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[align] wrote {json_dst}")

    # ---------- helpers ----------
    def _run(self, cmd: str, warn_only: bool = False):
        full_cmd = f". ./path.sh && . ./cmd.sh && {cmd}"
        print(f"[kaldi] {cmd}")
        result = subprocess.run(
            full_cmd,
            shell=True,
            cwd=self.recipe_dir,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0:
            if warn_only:
                print(f"[kaldi:warn] {result.stdout.strip()}")
            else:
                print(result.stderr)
                raise RuntimeError(f"Kaldi failed: {cmd}")
