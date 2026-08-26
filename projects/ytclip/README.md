# `ytclip` — descarga y recorte de audio

Paquete instalable (`uv sync` lo expone como comando `ytclip`). Antes se llamaba `kinai` y
además orquestaba un pipeline entero de Kaldi; esa parte está archivada en
[`../kaldi_asr/`](../kaldi_asr/).

```bash
ytclip where          # dónde está resolviendo las rutas
ytclip download       # descarga las fuentes y recorta cada segmento
ytclip correct        # editor interactivo de timestamps (TUI + reproducción)
ytclip gen-manifest   # aplana el manifiesto a un CSV de una fila por utterance
```

| Módulo | Qué hace |
| --- | --- |
| `download/audio_processor.py` | baja el audio con `yt-dlp` (o lo lee de disco) y recorta con `ffmpeg`, normalizando el pico |
| `editor/corpus_segment_editor.py` | TUI para ajustar `start`/`end` dígito a dígito escuchando el resultado |
| `manifest.py` | lee y escribe `source_segments.json` |
| `models/video_annotation.py` | `VideoAnnotation` / `Segment`, con timestamps `HH:MM:SS.mmm` |
| `paths.py` | envoltorio fino sobre `mayanlab.paths` |

## ⚠️ Limitación conocida

`download` y `correct` esperan el formato **antiguo** del manifiesto: una lista de vídeos
cuyos segmentos traen `maya` y `spanish`. El `source_segments.json` vigente es un dict de
tres grupos (`recordings`, `youtube`, `narraciones_mayas_campeche`) y no lleva texto, así
que `SpokenDictionaryManifest.__init__` falla al iterarlo.

Adaptar ese lector es lo único que falta para poder reconstruir el corpus entero desde un
clon limpio.
