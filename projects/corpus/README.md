# `corpus` — construcción del dataset · ACTIVO

Pipeline que va del audio crudo de tres fuentes al dataset publicado como
[`mau-cr/mayan-voice`](https://huggingface.co/datasets/mau-cr/mayan-voice): 2.535
utterances, 32 hablantes, ~4 h, mono 16 kHz. La ficha del dataset está en
[DATASET_CARD.md](DATASET_CARD.md).

## Notebooks, en orden

| Notebook | Qué hace |
| --- | --- |
| `00a_narraciones_download.ipynb` | descarga los 15 mp3 de las Narraciones Mayas de Campeche del sitio del INALI y calcula duraciones |
| `00b_narraciones_transcription_stubs.ipynb` | crea los `.txt` vacíos donde se transcribió a mano |
| `00c_narraciones_clean_text.ipynb` | normaliza las transcripciones originales (minúsculas, sin puntuación) para el LM |
| `0_segment_audios.ipynb` | recorta los mp3 largos en segmentos según `3h-transcripts.csv` |
| `1_merge_datasets.ipynb` | une YouTube + grabaciones propias + narraciones bajo `utt_id, maya, spk_id, filename` → `dataset.csv` |
| `2_transform_audio_names.ipynb` | renombra los wav al esquema canónico `spk_XXX_utt_YYYY` → `data/final/audio/` |
| `3_explore_dataset.ipynb` | integridad, duración por hablante y total, figura de distribución por género |
| `4_load_to_hugging_face.ipynb` | empaqueta y sube el dataset al Hub |
| `5_how_to_dataset.ipynb` | genera `source_segments.json`: el manifiesto de **procedencia del audio**, sin texto |
| `_correct_transcribe.ipynb` | corrección asistida de transcripciones con la API de Anthropic |

Ninguno tiene rutas relativas: todos importan de `mayanlab.paths`, así que se ejecutan
desde donde sea.

## El texto del subcorpus de 3 h

Las transcripciones alineadas de los 15 hablantes viven **en un solo sitio**,
`data/final/transcripts/`, con el mismo formato: un bloque por utterance separado por
línea en blanco, sin salto final.

Antes no era así. Los hablantes 04–15 tenían su `.txt`, pero **01–03 solo existían en la
columna `correction` de `3h-corrected-transcripts-manual.csv`**, y `1_merge_datasets` los
trataba como un caso especial. `scripts/build_3h_transcripts.py` materializó esos tres
archivos y valida que los 1.227 bloques coincidan exactamente con la columna `maya` de
`dataset.csv`:

```bash
python projects/corpus/scripts/build_3h_transcripts.py --check
```

Al unificarlo, `dataset.csv` se regenera idéntico salvo **una** celda: `spk_020_utt_0005`
perdió dos espacios finales, porque la rama de 01–03 era la única que no hacía `.strip()`.
El dataset publicado en el Hub todavía los tiene.

## Estado de ejecución de los notebooks

| Notebook | Estado |
| --- | --- |
| `00a_narraciones_download` | ejecutado — descarga los mp3 y los convierte a `data/work/narraciones_wav/` |
| `00b_narraciones_transcription_stubs` | ejecutado — **no sobrescribe** nada: si el `.txt` existe, lo deja intacto |
| `00c_narraciones_clean_text` | ejecutado |
| `0_segment_audios` | ejecutado — genera los 1.227 recortes en `data/work/3h-audios/` |
| `1_merge_datasets` | ejecutado — reproduce `dataset.csv` |
| `2_transform_audio_names` | **no se puede completar**: copia a `data/final/audio/` desde `work/3h-audios/` y `work/segments/`, y esta última está vacía porque `ytclip download` no lee el manifiesto vigente (ver abajo) |
| `3_explore_dataset` | ejecutado |
| `4_load_to_hugging_face` | **no ejecutado a propósito**: termina en `push_to_hub`, republicaría el dataset |
| `5_how_to_dataset` | ejecutado — regenera `source_segments.json` (requiere sesión de Hugging Face) |
| `_correct_transcribe` | **no ejecutado a propósito**: hace llamadas de pago a la API de Anthropic sobre los 1.227 segmentos |

## Fidelidad del recorte

`0_segment_audios` corta desde los wav que produce `00a`, **no** desde los mp3. No es un
detalle: `ffmpeg` con `-ss` antes de `-i` busca por frames en un mp3, y el decodificado
mete ruido de redondeo. Cortando desde el mp3 los 1.227 recortes salían con ~8 muestras
distintas de 233.984 (desviación máxima de 3 sobre ±32768: inaudible, pero no bit-exacto);
cortando desde el wav salen **byte a byte idénticos** al corpus publicado.

Verificado por md5 sobre los 1.227: **1.226 idénticos**. El único que difiere,
`spk_031_utt_0151`, difiere en **una sola muestra** (índice 96.466, t=6,029 s) y el
defecto está en el archivo publicado, no en el regenerado: sus vecinos van 903 → −1014 y
el valor publicado es −4249, un clic de una muestra. El regenerado da −134, que sí sigue
la señal.

## ⚠️ Lo que aún no es reproducible

`ytclip download` **no puede reconstruir el corpus todavía**. `SpokenDictionaryManifest`
espera el formato antiguo del manifiesto (una lista de vídeos con `maya`/`spanish`), y el
`source_segments.json` vigente es un dict de tres grupos sin texto. Hay que adaptar el
lector antes de que un clon limpio pueda regenerar el audio.

Tampoco están versionadas las 100 grabaciones propias (`spk_014`–`spk_018`): el manifiesto
las apunta a `final/audio/{utt_id}.wav`, pero ese audio no viaja con el repo.

## Pendiente de decidir

`spk_011` aparece como `xtiila` en la copia que había en `corpora/spk_metadata.csv` y como
`jtiila` en la de los notebooks. Se conservó **`jtiila`**, que es la que consumen los
notebooks y la que produjo el dataset publicado.
