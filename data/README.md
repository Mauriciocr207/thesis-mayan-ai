# `data/` — todos los datos del proyecto

Raíz única. Por defecto es `<repo>/data`; se puede mover a otro disco definiendo
`MAYAN_DATA` en `.env`. **Ningún notebook ni script tiene rutas propias**: todos
resuelven desde `mayanlab.paths`, así que cambiar esa variable los reapunta a todos.

```python
from mayanlab.paths import AUDIO, ANNOTATIONS, MANIFESTS, TRANSCRIPTS
```

## Organización: fuente → producido

| Carpeta | Qué es | ¿Se edita? |
| --- | --- | --- |
| `source/` | lo que vino de fuera, tal como se obtuvo | nunca |
| `work/` | intermedios regenerables | se puede borrar entera |
| `final/` | lo que produce el proyecto | solo desde los notebooks |

```
source/
├── youtube/                 44 wav de los vídeos didácticos (2,8 G)
├── narraciones_inali/
│   ├── mp3/                 15 mp3 originales del INALI
│   └── transcripts/         transcripciones originales, con puntuación
├── recordings/              grabaciones propias por hablante (incluye .aup3 de Audacity)
├── global_recordings_net/   mp3 de globalrecordings.net
├── mms/                     muestras del corpus MMS ulab
└── annotations/             anotación manual (csv/json, versionados)

work/                        REGENERABLE — nada aquí es fuente de verdad
├── segments/                salida de `ytclip download`
├── narraciones_clean_text/  salida de projects/kaldi_asr/scripts/normalize_narraciones.py
└── orphan_segments/         2 segmentos que se recortaron pero no llegaron al corpus

final/
├── audio/                   2.535 wav `spk_XXX_utt_YYYY.wav` = dataset `mau-cr/mayan-voice`
├── transcripts/             15 .txt alineados del subcorpus de 3 h (uno por narración)
├── lm_text/                 texto corrido para el modelo de lenguaje + mayan_bible.txt
└── manifests/               dataset.csv, final_dataset*.csv, source_segments.json, …
```

## Qué se versiona

Dentro de `data/` **se versiona todo salvo los formatos pesados** (`*.wav`, `*.mp3`,
`*.aup3`, `*.npz`, shapefiles) y `work/` entera. Son ~1 MB de texto y tablas: lo justo
para reconstruir el corpus desde un clon limpio sin arrastrar los 3,7 GB de audio.

> ⚠️ `source/annotations/spk_metadata.csv` mapea `spk_id` → nombre real de la persona.
> **No publicarlo** junto al dataset.

> Las transcripciones del INALI (`final/transcripts/`, `source/narraciones_inali/`) están
> versionadas. Si prefieres sacarlas de git por los derechos sobre el texto —la misma razón
> por la que `source_segments.json` va sin transcripciones—, añade sus rutas a `.gitignore`.

## Cómo regenerar lo que no está

| Falta | Cómo se recupera |
| --- | --- |
| `source/youtube/*.wav` | `yt-dlp` con las urls de `final/manifests/source_segments.json` |
| `source/narraciones_inali/mp3/` | `projects/corpus/notebooks/00a_narraciones_download.ipynb` (los descarga del sitio del INALI) |
| wav a partir de un mp3 | `ffmpeg -i x.mp3 -ac 1 -ar 16000 x.wav` |
| `work/segments/` | `ytclip download` (⚠ ver la limitación en `projects/corpus/README.md`) |
| `work/narraciones_clean_text/` | `python projects/kaldi_asr/scripts/normalize_narraciones.py` |
| `final/audio/` | `projects/corpus/notebooks/` 0 → 2, o bajando el dataset del Hub |
| `final/transcripts/{01,02,03}` | `python projects/corpus/scripts/build_3h_transcripts.py` |

Las **grabaciones propias** (`spk_014`–`spk_018`) no se pueden recuperar de ninguna
fuente pública: `source/recordings/` es su único origen.
