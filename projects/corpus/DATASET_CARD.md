---
language:
  - yua
  - es
license: cc-by-nc-sa-4.0
pretty_name: Mayan Voice
size_categories:
  - 1K<n<10K
task_categories:
  - automatic-speech-recognition
tags:
  - speech
  - asr
  - low-resource
  - maya
  - yucatec-maya
  - indigenous-language
  - mexico
  - yucatan
  - campeche
configs:
  - config_name: default
    data_files:
      - split: train
        path: data/train-*
---

# Mayan Voice

Corpus de audio + transcripción en **maya yucateco (yua)** compilado para el entrenamiento y evaluación de modelos de reconocimiento automático del habla (ASR) en lenguas indígenas de baja densidad de recursos. Forma parte del trabajo de tesis sobre ASR para maya yucateco modelos basados en MMS.

- **Idioma:** Maya yucateco (ISO 639-3: `yua`), con glosas/contexto en español.
- **Modalidad:** Audio mono, 16 kHz, transcripción ortográfica en maya.
- **Tamaño:** 2,535 utterances.
- **Hablantes:** 32 hablantes únicos (`spk_001`–`spk_032`).

## Acceso

🔒 **El repositorio está privado por el momento.** Para usar el corpus hay que **solicitar
los datos** al autor (ver [Contacto](#contacto)) y, con el acceso concedido, autenticarse:

```bash
huggingface-cli login          # sin token autorizado, load_dataset responde 401
```

El modelo entrenado con este corpus sí es público y se puede probar sin pedir nada:

- 💬 **[Kinai](https://asr-maya-chatbot.netlify.app)** — el chatbot con el modelo aplicado:
  se le habla en maya yucateco, transcribe y responde en la conversación.
- 🚀 **[Space de Gradio](https://huggingface.co/spaces/mau-cr/asr-maya-yucateco)** — la demo
  de transcripción sola.
- 🤗 **[`mau-cr/mayan_best_model`](https://huggingface.co/mau-cr/mayan_best_model)** — los
  pesos (MMS-1b-all ajustado con adapters, 240 min + LM de 3 gramas).
- 🎥 **[Video de la demostración](https://www.youtube.com/watch?v=3JNS1Rq7eg0)**
- 💻 **[Repositorio de la tesis](https://github.com/Mauriciocr207/thesis-mayan-ai)**

## Composición

El dataset agrega varias fuentes de habla en maya yucateco:

| Subcorpus | Hablantes | Duración aprox. | Fuente |
|---|---|---|---|
| Narraciones Mayas de Campeche | `spk_019` – `spk_032` | ~3 h | Narraciones orales de hablantes nativos de Campeche |
| YouTube (canales educativos / culturales) | `spk_001` – `spk_013` | ~1 h | Material público de YouTube |
| Grabaciones locales | `spk_014` – `spk_018` | breve | Grabaciones propias con hablantes locales |

### Canales de YouTube incluidos

- **Filosofía Maya** — <https://www.youtube.com/channel/UCZn6vRtgReGb0osqkybFjrA>
  Serie "Aprenda Maya" (alfabeto, frases 1–31, diálogos 1–6).
- **LENGUA Y CULTURA MAYA YUCATECA** — <https://www.youtube.com/channel/UCqAVUjjtvCXXu3mBTwNVFXw>
  Colores, partes del cuerpo, animales, presentaciones, construcción de frases.
- **Lengua Maya Yucateco con Maestro Pat** — <https://www.youtube.com/channel/UCTHxb-dpdb6-skKKZoahAww>
  Frases comunes en lengua maya.
- **YazzNovelo** — <https://www.youtube.com/channel/UCFZzWp9LwVPO5r0kLQYWBXg>
  Saludos y despedidas en maya yucateco.
- **Jose Javier May Chan** — <https://www.youtube.com/channel/UCst32JEdj2Jsiw9HH_1rBfQ>
  *Bix a beel: ¿Cómo estás?*

Los segmentos extraídos de YouTube fueron recortados manualmente y transcritos en ortografía estándar del maya yucateco.

## Estructura

Cada ejemplo tiene los siguientes campos:

| Campo   | Tipo               | Descripción |
|---------|--------------------|-------------|
| `audio` | `Audio(16000 Hz)`  | Forma de onda mono a 16 kHz. |
| `maya`  | `string`           | Transcripción ortográfica en maya yucateco. |
| `utt_id`| `string`           | Identificador único del utterance (`spk_XXX_utt_YYYY`). |
| `spk_id`| `string`           | Identificador del hablante. |

Split disponible: `train` (2,535 ejemplos).

## Uso

Requiere acceso concedido y sesión iniciada (ver [Acceso](#acceso)).

```python
from datasets import load_dataset

ds = load_dataset("mau-cr/mayan-voice", split="train")
print(ds[0]["maya"])
# 'baach'

sample = ds[0]
audio = sample["audio"]["array"]
sr = sample["audio"]["sampling_rate"]  # 16000
```

Ejemplo mínimo de fine-tuning con `transformers` (MMS / Wav2Vec2):

```python
from datasets import load_dataset, Audio

ds = load_dataset("mau-cr/mayan-voice", split="train")
ds = ds.cast_column("audio", Audio(sampling_rate=16_000))
ds = ds.train_test_split(test_size=0.1, seed=42)
```

## Hablantes

| spk_id | Origen | Sexo |
|--------|--------|------|
| spk_001 | Canal: Filosofía Maya | mujer |
| spk_002 | Canal: Lengua y Cultura Maya Yucateca | hombre |
| spk_003 | Canal: Lengua y Cultura Maya Yucateca | hombre |
| spk_004 | Canal: Lengua y Cultura Maya Yucateca | mujer |
| spk_005 | Canal: Lengua Maya Yucateco con Maestro Pat | hombre |
| spk_006 | Canal: Filosofía Maya | mujer |
| spk_007 | Canal: YazzNovelo | mujer |
| spk_008 | Canal: Filosofía Maya | hombre |
| spk_009 | Canal: Filosofía Maya (*jkalin*) | hombre |
| spk_010 | Canal: Filosofía Maya (*jsaan*) | hombre |
| spk_011 | Canal: Filosofía Maya (*xtiila*) | mujer |
| spk_012 | Canal: Filosofía Maya (*xsees*) | mujer |
| spk_013 | Canal: Filosofía Maya (*jmiilo*) | hombre |
| spk_014 | Grabaciones propias: spk_014 | mujer |
| spk_015 | Grabaciones propias: spk_015 | mujer |
| spk_016 | Grabaciones propias: spk_016 | hombre |
| spk_017 | Grabaciones propias: spk_017 | hombre |
| spk_018 | Grabaciones propias: spk_018 | hombre |
| spk_019 | Narraciones Mayas de Campeche: Anatolio Pech | hombre |
| spk_020 | Narraciones Mayas de Campeche: Liboria May | mujer |
| spk_021 | Narraciones Mayas de Campeche: Eligio Uicab | hombre |
| spk_022 | Narraciones Mayas de Campeche: Alfonso Tamay | hombre |
| spk_023 | Narraciones Mayas de Campeche: Felipe May | hombre |
| spk_024 | Narraciones Mayas de Campeche: Gricelda Pech | mujer |
| spk_025 | Narraciones Mayas de Campeche: Teodoro May | hombre |
| spk_026 | Narraciones Mayas de Campeche: Adolfo Chuc | hombre |
| spk_027 | Narraciones Mayas de Campeche: Jesús Euan | hombre |
| spk_028 | Narraciones Mayas de Campeche: Héctor May | hombre |
| spk_029 | Narraciones Mayas de Campeche: Lourdes y Marcela Ucam | mujer |
| spk_030 | Narraciones Mayas de Campeche: Venustiano Puc | hombre |
| spk_031 | Narraciones Mayas de Campeche: Micaela Ek | mujer |
| spk_032 | Narraciones Mayas de Campeche: Mario Chan | hombre |

## Recolección y procesado

1. **Selección de fuentes** con consentimiento o licencia pública.
2. **Extracción de audio** de los videos de YouTube y normalización a WAV mono 16 kHz.
3. **Segmentación manual** de utterances con un selector de spans propio.
4. **Transcripción** en ortografía estándar del maya yucateco, revisada manualmente.

## Limitaciones y consideraciones

- El corpus mezcla **registros muy distintos**: material didáctico estructurado (YouTube), grabaciones locales en condiciones variables y narraciones orales tradicionales. El dominio acústico y léxico no es homogéneo.
- Hay **desbalance entre hablantes** y entre subcorpus (Narraciones Mayas de Campeche aporta la mayor parte de la duración).
- La transcripción usa ortografía estándar, pero puede contener inconsistencias propias de la **variación dialectal** del maya yucateco entre Yucatán, Campeche y Quintana Roo.
- Los segmentos de YouTube provienen de material público con fines educativos; se incluyen aquí para investigación no comercial.
- **No es un corpus de evaluación general**: el split disponible es solo `train`. Para benchmarking conviene construir splits propios estratificando por hablante y subcorpus.

## Licencia

Distribuido bajo **CC BY-NC-SA 4.0**. Uso permitido para investigación y fines no comerciales, con atribución y bajo la misma licencia. El material derivado de YouTube se incluye al amparo del uso justo con fines educativos y de investigación; los derechos del audio original pertenecen a sus respectivos canales.

## Cita

Si usas este dataset, por favor cita:

```bibtex
@misc{mayanvoice2026,
  title        = {Mayan Voice: A speech corpus for Yucatec Maya ASR},
  author       = {Carrillo Romero, Mauricio},
  year         = {2026},
  howpublished = {Hugging Face Datasets},
  url          = {https://huggingface.co/datasets/mau-cr/mayan-voice}
}
```

## Agradecimientos

A los hablantes nativos que prestaron su voz, a los creadores de los canales de YouTube por mantener material educativo en maya yucateco accesible, y al proyecto *Narraciones Mayas de Campeche* por sus narraciones orales.

## Contacto

Para **solicitar acceso al corpus** o cualquier duda sobre el dataset:

- Autor: Mauricio Carrillo Romero
- Email: enrique.mauricio.carrillo.romero@gmail.com
- Hugging Face: <https://huggingface.co/mau-cr>
- Repositorio: <https://github.com/Mauriciocr207/thesis-mayan-ai>
