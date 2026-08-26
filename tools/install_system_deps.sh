#!/usr/bin/env bash
# Dependencias del SISTEMA (las de Python las gestiona `uv sync`).
#
#   ./tools/install_system_deps.sh --check   # solo informa de qué falta
#   ./tools/install_system_deps.sh           # instala el grupo base
#   ./tools/install_system_deps.sh --all     # base + KenLM + Node (speech-collector)
#
# Ver la tabla de qué necesita cada cosa en tools/README.md.
set -euo pipefail

# Grupo base: lo que necesitan el corpus, el análisis y ytclip.
BASE_PKGS=(
  ffmpeg              # recorte y conversión de audio; ffprobe para duraciones
  libespeak-ng1       # backend de phonemizer para préstamos del español
  espeak-ng-data      # voces de espeak-ng
  portaudio19-dev     # sounddevice: reproducir audio en `ytclip correct`
  python3-tk          # backend interactivo de matplotlib en el editor de segmentos
)

# Solo para compilar KenLM (tools/install_kenlm.sh).
KENLM_PKGS=(
  build-essential cmake libboost-all-dev libeigen3-dev
  zlib1g-dev libbz2-dev liblzma-dev
)

# Opcional: festival solo fonemiza inglés. El tokenizador usa espeak, no festival.
# Se instala únicamente si quieres la celda comparativa de dataset_tokenizer.ipynb.
OPT_PKGS=(festival)

check() {
  local fallan=0
  echo "--- binarios ---"
  for b in ffmpeg ffprobe; do
    printf '  %-22s' "$b"
    if command -v "$b" >/dev/null; then echo "ok"; else echo "FALTA"; fallan=1; fi
  done

  echo "--- librerías ---"
  printf '  %-22s' "libespeak-ng"
  if ldconfig -p 2>/dev/null | grep -q libespeak-ng; then echo "ok"; else echo "FALTA"; fallan=1; fi

  echo "--- backends de phonemizer ---"
  # Preferimos el intérprete del proyecto; si no hay entorno, avisamos.
  PY_RUN=(python); command -v uv >/dev/null && PY_RUN=(uv run --quiet python)
  "${PY_RUN[@]}" - <<'PY' 2>/dev/null || echo "  (entorno de Python no disponible: corre 'uv sync' primero)"
from phonemizer.backend import BACKENDS
for name in ("espeak", "festival"):
    try:
        b = BACKENDS[name]
        langs = b.supported_languages()
        print(f"  {name:<20} ok  ({len(langs)} idiomas, español: {'es' in langs})")
    except Exception as exc:
        print(f"  {name:<20} no disponible: {type(exc).__name__}")
PY

  echo "--- opcionales ---"
  for b in festival node pnpm psql cmake; do
    printf '  %-22s' "$b"
    command -v "$b" >/dev/null && echo "ok" || echo "no instalado"
  done

  echo
  [ "$fallan" -eq 0 ] && echo "Las dependencias obligatorias están cubiertas." \
                      || echo "Faltan dependencias obligatorias: corre este script sin --check."
  return 0
}

install_node() {
  export NVM_DIR="$HOME/.nvm"
  if [ ! -s "$NVM_DIR/nvm.sh" ]; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
  fi
  # shellcheck disable=SC1091
  [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
  nvm install --lts && nvm use --lts
  corepack enable && corepack prepare pnpm@latest --activate
  echo "Node $(node -v) y pnpm $(pnpm -v) listos. Recarga la terminal para tenerlos en el PATH."
}

case "${1:-}" in
  --check) check; exit 0 ;;
  --all)   sudo apt update
           sudo apt install -y "${BASE_PKGS[@]}" "${KENLM_PKGS[@]}" "${OPT_PKGS[@]}"
           install_node ;;
  "")      sudo apt update
           sudo apt install -y "${BASE_PKGS[@]}" ;;
  *)       echo "uso: $0 [--check|--all]" >&2; exit 2 ;;
esac

echo
echo "Listo. Comprueba el estado con: $0 --check"
