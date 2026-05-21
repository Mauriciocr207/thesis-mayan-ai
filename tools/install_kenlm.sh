#!/usr/bin/env bash
# Compila KenLM con soporte de entrenamiento (lmplz, build_binary).
# Requiere: cmake, libboost-all-dev, libeigen3-dev, build-essential, zlib1g-dev, libbz2-dev, liblzma-dev.
# Binarios quedan en tools/kenlm/build/bin/. Añádelos al PATH o usa ruta absoluta.
set -e
cd "$(dirname "$0")"

if [ ! -d kenlm ]; then
  git clone https://github.com/kpu/kenlm.git
fi

cd kenlm
mkdir -p build
cd build
cmake ..
make -j"$(nproc)"

echo
echo "[install_kenlm] OK. Binarios en: $(pwd)/bin"
echo "[install_kenlm] Añade al PATH: export PATH=\"$(pwd)/bin:\$PATH\""
