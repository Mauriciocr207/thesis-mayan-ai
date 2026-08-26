# `tools/` — dependencias externas y del sistema

Nada de lo compilado aquí se versiona: son builds locales, pesados y reproducibles con los
scripts de esta misma carpeta.

| Carpeta | Qué es | Cómo se obtiene |
| --- | --- | --- |
| `kaldi/` | clon de [kaldi-asr/kaldi](https://github.com/kaldi-asr/kaldi) ya compilado (~9,7 G) | `install_kaldi.sh` — **pendiente de escribir**; hoy hay que seguir el `INSTALL` de Kaldi a mano |
| `kenlm/` | [KenLM](https://github.com/kpu/kenlm) compilado, para `lmplz` / `build_binary` | `./install_kenlm.sh` |

## Dependencias del sistema

Lo que `uv sync` **no** instala, porque no son paquetes de Python. Se instalan y comprueban
con `tools/install_system_deps.sh`:

```bash
./tools/install_system_deps.sh --check   # informa de qué falta
./tools/install_system_deps.sh           # instala el grupo obligatorio
./tools/install_system_deps.sh --all     # además KenLM y Node
```

### Obligatorias

| Paquete apt | Para qué | Se rompe si falta |
| --- | --- | --- |
| `ffmpeg` | recorte y conversión de audio; `ffprobe` para duraciones | `ytclip download`, `0_segment_audios`, `00a_narraciones_download`, `dataset_length` |
| `libespeak-ng1` + `espeak-ng-data` | backend de `phonemizer` para los préstamos del español | `MayaPhonemeTokenizer.tokenize()` con cualquier palabra fuera de la tabla g2p maya — el 13,9 % del vocabulario del corpus |
| `portaudio19-dev` | `sounddevice`, reproducir audio | `ytclip correct` |
| `python3-tk` | backend interactivo de matplotlib | `ytclip correct` (usa `matplotlib.widgets.Button`) |

> `libespeak-ng1` es una **librería**, no el binario `espeak-ng`: `phonemizer` la carga por
> `ctypes`, así que `which espeak-ng` puede no encontrar nada y aun así funcionar.

### Opcionales

| Paquete | Para qué |
| --- | --- |
| `festival` | **solo fonemiza inglés.** El tokenizador usa espeak, no festival. Solo hace falta para la celda comparativa de `dataset_tokenizer.ipynb` |
| `build-essential cmake libboost-all-dev libeigen3-dev zlib1g-dev libbz2-dev liblzma-dev` | compilar KenLM con `install_kenlm.sh` |
| Node LTS + pnpm (vía nvm) | `projects/speech-collector/` |
| PostgreSQL | `projects/speech-collector/` |

### Credenciales

| Variable | Para qué |
| --- | --- |
| sesión de Hugging Face (`huggingface-cli login`) | `4_load_to_hugging_face`, `5_how_to_dataset` |
| `ANTHROPIC_API_KEY` en `.env` | `_correct_transcribe` |
| `MAYAN_DATA` en `.env` (opcional) | mover la raíz de datos a otro disco |

## Compilados externos

La receta archivada de Kaldi (`projects/kaldi_asr/recipe/`) apunta aquí con enlaces
simbólicos **relativos**, así que funciona esté donde esté clonado el repo:

```bash
cd projects/kaldi_asr/recipe && . ./path.sh && which compute-mfcc-feats
```
