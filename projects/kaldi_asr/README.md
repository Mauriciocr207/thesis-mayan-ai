# `kaldi_asr` — pipeline con Kaldi · ARCHIVADO

El primer camino del proyecto: replicar a Bartley & Ragni con Kaldi (alineamiento forzado,
mono/tri, lexicón, LM de n-gramas). Se abandonó al pasar a fine-tuning de MMS. **No está en
uso**, pero se conserva entero y funcional en lo estructural para poder retomarlo.

## Qué hay

| Carpeta | Contenido |
| --- | --- |
| `recipe/` | receta al estilo `egs/`: `cmd.sh`, `path.sh`, `conf/`, `data/`, `exp/` y los enlaces `steps`/`utils` |
| `lexicon/` | lexicón compartido: `lexicon.txt`, `nonsilence_phones.txt`, `silence_phones.txt`, `optional_silence.txt` |
| `legacy/` | el código Python de la etapa Kaldi + el `source_segments.json` en formato antiguo (con `maya`/`spanish`) |
| `scripts/` | los `.sh` de entrenamiento y decodificación, más `generate_metrics.py`, `align_metrics.py`, `pad_segments.py`, `normalize_narraciones.py` |

## Que sigue funcionando

Los enlaces a Kaldi son **relativos** y `path.sh` deduce `KALDI_ROOT` de su propia
ubicación, así que la receta encuentra los binarios esté donde esté el repo:

```bash
cd projects/kaldi_asr/recipe && . ./path.sh && which compute-mfcc-feats
```

`legacy/paths.py` reconstruye el objeto `Paths` que esperaba el pipeline, ya resuelto sobre
la estructura nueva de `data/`.

## Qué falta para revivirlo

1. **`tools/install_kaldi.sh` está vacío.** La compilación de Kaldi es manual hoy.
2. **La mitad del CLI nunca se terminó.** `train`, `align`, `segment`, `build_lm` y
   `gen_lexicon` ya eran cuerpos comentados cuando se archivó; el código que invocaban sí
   está aquí, en `legacy/corpus_pipeline/`.
3. Los `.sh` de `scripts/` traen `KALDI_ROOT=/path/to/kaldi  # AJUSTA ESTO` sin resolver.
4. `legacy/` no está declarado como paquete instalable: para importarlo hay que añadir
   `projects/kaldi_asr/` al `sys.path`.
5. `legacy/corpus_pipeline/kaldi_data_builder.py:100` llama a `tokenizer.tokenize_word()`,
   que **no existe**: el método es `_tokenize_word` (privado) y el público es `tokenize`.
   Ya estaba roto antes de archivarlo.
