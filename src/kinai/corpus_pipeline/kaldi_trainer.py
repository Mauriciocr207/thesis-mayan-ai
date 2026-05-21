import subprocess
from kinai.classes.paths import Paths


class KaldiTrainer:
    """Ejecuta los pasos de entrenamiento de Kaldi desde el recipe."""

    def __init__(self, paths: Paths, experiment: str, nj: int = 1):
        self.paths = paths
        self.recipe_dir = paths.recipe_dir
        self.experiment = experiment
        self.nj = nj

    def train(self):
        if not self.recipe_dir.exists():
            raise RuntimeError(
                f"Recipe dir not found: {self.recipe_dir}\n"
                "Run 'kinai gen-train-data' first."
            )
        self._prepare_lang()
        self._prepare_data()
        self._extract_features()
        self._train_model()

    def _run(self, cmd: str, warn_only: bool = False):
        """Ejecuta un comando bash dentro del recipe_dir con path.sh y cmd.sh cargados."""
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

    def _prepare_lang(self):
        self._run(
            'utils/prepare_lang.sh data/local/lang "<unk>" data/local/lang_tmp data/lang'
        )

    def _prepare_data(self):
        self._run("utils/fix_data_dir.sh data/train")
        self._run("utils/validate_data_dir.sh data/train --no-feats", warn_only=True)

    def _extract_features(self):
        self._run("steps/make_mfcc.sh --nj 1 --cmd run.pl data/train")
        self._run("steps/compute_cmvn_stats.sh data/train")
        self._run("utils/fix_data_dir.sh data/train")
        self._run("utils/validate_data_dir.sh data/train", warn_only=True)

    def _train_model(self):
        nj = self.nj
        train_commands = {
            "mono": (
                f"steps/train_mono.sh --boost-silence 1.25 --nj {nj} --cmd run.pl "
                "data/train data/lang exp/mono"
            ),
            "tri": (
                f"steps/align_fmllr.sh --nj {nj} --cmd run.pl "
                "data/train data/lang exp/mono exp/mono_ali && "
                f"steps/train_deltas.sh --cmd run.pl 2000 10000 "
                "data/train data/lang exp/mono_ali exp/tri"
            ),
            "tdnn": (
                f"steps/align_si.sh --nj {nj} --cmd run.pl "
                "data/train data/lang exp/tri exp/tri_ali && "
                f"steps/train_lda_mllt.sh --cmd run.pl 2500 15000 "
                "data/train data/lang exp/tri_ali exp/tdnn"
            ),
        }

        cmd = train_commands.get(self.experiment)
        if cmd is None:
            raise ValueError(
                f"Experiment '{self.experiment}' not supported. "
                f"Options: {list(train_commands.keys())}"
            )
        self._run(cmd)
