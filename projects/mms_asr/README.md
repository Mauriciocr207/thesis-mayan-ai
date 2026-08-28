# `mms_asr` — fine-tuning de MMS-1b-all · ACTIVO

El experimento central de la tesis: ajustar los adapters de lengua de
[`facebook/mms-1b-all`](https://huggingface.co/facebook/mms-1b-all) sobre `yua` y trazar
la curva de aprendizaje de 20 a 240 minutos.

| Notebook | Dónde corre |
| --- | --- |
| `fine_tune_adapter_mms.ipynb` | **Google Colab con GPU** |
| `generate_wer_lm_graphic.ipynb` | local; escribe en `results/` |

## Cómo corre en Colab

El notebook **no lee `data/`**: carga el corpus desde el Hub (`mau-cr/mayan-voice`), así
que no hace falta subir audio. Ese repositorio está **privado por el momento**, así que la
celda de carga necesita un token con acceso concedido (`huggingface-cli login` o
`login()` de `huggingface_hub`); el acceso se pide al autor. Lo que sí usa de Drive:

```
/content/drive/MyDrive/thesis-mayan-ai/
├── vocab/vocab.json
├── kenlm/build/bin/          # lmplz, build_binary
└── language_model/           # train_dataset_lm.txt, lm_3gram.arpa
```

Si en algún momento necesitas que el notebook lea datos locales, define la raíz antes de
importar nada del proyecto:

```python
import os
os.environ["MAYAN_DATA"] = "/content/drive/MyDrive/thesis-mayan-ai/data"
```

## Qué produce

- 12 modelos, uno por punto de la curva: `mau-cr/mms-maya-020min` … `mau-cr/mms-maya-240min`
- `mau-cr/mayan_best_model` — 240 min + LM, empaquetado con su processor
- `mau-cr/mms_yua_results` — métricas de la curva
- `results/wer_vs_audio_minutes.{svg,pdf}`

| Configuración | Valor |
| --- | --- |
| Test | `spk_002`, `spk_020`, `spk_024`, `spk_028` (~24 min) |
| Validación | `spk_009`, `spk_029` (~15 min) |
| Hiperparámetros | lr=1e-3, epochs=40, batch=32, fp16, warmup=100, gradient checkpointing |
| Decoder | KenLM 3-gramas + beam search (pyctcdecode), grid search de (α, β) |
