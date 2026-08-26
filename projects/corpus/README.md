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
