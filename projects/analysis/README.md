# `analysis` — análisis lingüístico y acústico · ACTIVO

De aquí salen la mayoría de las figuras de la tesis. Todo lee del corpus ya construido
(`data/final/`) y escribe en `figures/` y `features/` de este proyecto.

| Notebook | Qué produce |
| --- | --- |
| `analyze_lexico.ipynb` | distribución de palabras, n-gramas, bigramas C/V, mapas de calor CV/CVC |
| `analyze_acoustic.ipynb` | formantes, espacio vocálico (raw, k-means, DBSCAN), F0 por sexo, espectrogramas — vía Praat/parselmouth |
| `analyze_yt_audios.ipynb` | composición del subcorpus de YouTube |
| `analyze_narraciones_maya_campeche.ipynb` | composición del subcorpus del INALI |
| `analyze_mms.ipynb` | exploración del corpus MMS ulab v2 de Meta |
| `mayan_statistics.ipynb` | estadística sociolingüística con datos del INEGI |
| `spectrogram.ipynb` | forma de onda, espectrograma, intensidad y MFCC de una utterance |
| `dataset_length.ipynb` | duración total del corpus |
| `dataset_tokenizer.ipynb` | pruebas del tokenizador fonémico maya (`mayanlab.tokenizer`) |
| `word_counter.ipynb` | conteo de palabras |
| `segmented_audio_duration.ipynb` | duración cubierta por los segmentos del manifiesto antiguo |

`analyze_acoustic.ipynb` recalcula formantes sobre las 2.535 utterances y tarda; la celda
siguiente reutiliza `features/formants.npz` si ya está.

Todos están ejecutados.

`dataset_tokenizer.ipynb` necesita `libespeak-ng1` + `espeak-ng-data`: el tokenizador cae a
`phonemizer`/espeak para los préstamos del español, que son el **13,9 % del vocabulario del
corpus** (809 de 5.802 palabras únicas). La celda que compara backends también usa
`festival`, que solo fonemiza inglés y es opcional. Todo eso se instala y comprueba con
`./tools/install_system_deps.sh`.
