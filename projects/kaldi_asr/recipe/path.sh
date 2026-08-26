# Relativo a esta receta, para que no dependa de dónde esté clonado el repo.
export KALDI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../tools/kaldi" && pwd)"
[ -f $KALDI_ROOT/tools/env.sh ] && . $KALDI_ROOT/tools/env.sh
export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$PWD:$PATH
[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && echo >&2 "common_path.sh not found" && exit 1
. $KALDI_ROOT/tools/config/common_path.sh
export LC_ALL=C
export PYTHONUNBUFFERED=1
