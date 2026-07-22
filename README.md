# 🪶 thesis-mayan-ai

[![Hugging Face Dataset](https://img.shields.io/badge/🤗%20Dataset-mau--cr%2Fmayan--voice-FFD21E?style=for-the-badge)](https://huggingface.co/datasets/mau-cr/mayan-voice)
[![Hugging Face Model](https://img.shields.io/badge/🤗%20Model-mayan__best__model-FFD21E?style=for-the-badge)](https://huggingface.co/mau-cr/mayan_best_model)
[![Gradio Demo](https://img.shields.io/badge/🚀%20Demo-Gradio%20Space-FF7C00?style=for-the-badge&logo=gradio)](https://huggingface.co/spaces/mau-cr/asr-maya-yucateco)

![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-EE4C2C?style=for-the-badge&logo=pytorch)
![Transformers](https://img.shields.io/badge/🤗%20Transformers-MMS--1b--all-FFD21E?style=for-the-badge)
![KenLM](https://img.shields.io/badge/KenLM-3--gram%20LM-6E40C9?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active%20Development-success?style=for-the-badge)

## 🌟 Descripción del proyecto

**thesis-mayan-ai** es el repositorio activo de mi tesis sobre **reconocimiento automático del habla (ASR) en maya yucateco**. Reúne dos líneas de trabajo que se sostienen mutuamente: la construcción y análisis de un **corpus propio** de aproximadamente cuatro horas de audio etiquetado, y el **ajuste fino del modelo multilingüe [MMS-1b-all](https://huggingface.co/facebook/mms-1b-all)** de Meta sobre ese corpus para trazar una curva de aprendizaje que responda la pregunta de fondo: ¿cuánto audio necesita el maya yucateco para un ASR usable?

> 📚 **Pregunta de investigación**: La lógica experimental replica a [Bartley y Ragni (2025)](https://arxiv.org/abs/2510.04832), quienes mostraron que con apenas 40 minutos de audio bien curado se puede entrenar un ASR funcional para lenguas críticamente en peligro. En este caso se explora el uso de un **modelo preentrenado moderno** ajustado vía **adapters de lengua** sobre el código ISO `yua` (Maya Yucateco).

> 🧭 **Nota**: El repositorio conserva material exploratorio (pipeline con Kaldi, herramientas de grabación, scripts sueltos) como bitácora del proceso. No todo está en uso activo; las secciones lo indican explícitamente.

## 🔗 Recursos

| Recurso | Ubicación |
| --- | --- |
| 🎙️ **Corpus** | [`mau-cr/mayan-voice`](https://huggingface.co/datasets/mau-cr/mayan-voice) |
| 📊 **Modelos por punto de curva** | `mau-cr/mms-maya-020min` … [`mau-cr/mms-maya-240min`](https://huggingface.co/mau-cr/mms-maya-240min) |
| 🏆 **Mejor modelo (240 min + LM)** | [`mau-cr/mayan_best_model`](https://huggingface.co/mau-cr/mayan_best_model) |
| 📈 **Resultados de scaling** | [`mau-cr/mms_yua_results`](https://huggingface.co/datasets/mau-cr/mms_yua_results) |
| 🌐 **Demo interactiva** | _(TBD — Hugging Face Space con Gradio)_ |
| 📄 **Paper de referencia** | [Bartley & Ragni, 2025](https://arxiv.org/abs/2510.04832) |

## 🎯 Principales características

- **🎙️ Corpus propio de maya yucateco** — ~2,535 utterances de 32 hablantes, ~4 horas, mono a 16 kHz, integrando fuentes diversas (YouTube didáctico, narraciones de Maya Campeche, grabaciones propias).
- **📈 Curva de aprendizaje completa** — Doce modelos entrenados de 20 a 240 minutos en pasos de 20, todos con la misma semilla y subsets anidados para que la variable independiente sea estrictamente la cantidad de audio.
- **🧩 Fine-tuning con adapters** — Solo se ajustan los módulos de lengua sobre MMS-1b-all; el backbone preentrenado queda congelado, lo que permite entrenar la curva entera con costo computacional razonable.
- **🔤 Decodificación con modelo de lenguaje** — KenLM de 3-gramas más beam search vía `pyctcdecode`, con grid search de hiperparámetros (α, β) sobre el set de validación.
- **👥 Splits por hablante** — Test y validación con hablantes hold-out fijos para que las métricas no se inflen por memorización de timbres.
- **📊 Análisis lingüístico y acústico** — Espacio vocálico, formantes, F0, distribuciones de n-gramas, mapas de calor CV/CVC, todo reproducible desde notebooks.

## 🧠 Metodología

### El punto de partida: MMS ulab v2 y MMS-1b-all

**MMS ulab v2** es el corpus multilingüe no etiquetado construido por Meta dentro del proyecto _Scaling Speech Technology to 1000+ Languages_. Reúne ~8,900 horas en 4,023 lenguas de 189 familias lingüísticas, incluyendo el maya yucateco. Una porción de este corpus se utilizó para preentrenar la familia **MMS** de modelos acústicos, lo que vuelve a MMS-1b-all un punto de partida natural para el maya: aunque nunca haya visto transcripciones, ya tiene representaciones internas razonables para los sonidos de la lengua.

### Ajuste fino con adapters

En lugar de actualizar los miles de millones de parámetros del modelo base, el entrenamiento **congela toda la base preentrenada** y solo ajusta los adapters de la lengua objetivo (`target_lang="yua"`), siguiendo la estrategia que Mainzinger y Levow (2024) reportan como la más adecuada para lenguas de bajos recursos:

```python
model.init_adapter_layers()
model.freeze_base_model()
for name, param in model._get_adapters().items():
    param.requires_grad = True
```

### La curva de aprendizaje

| Componente | Configuración |
| --- | --- |
| **Modelo base** | `facebook/mms-1b-all` |
| **Lengua objetivo** | Maya yucateco (`yua`) |
| **Puntos de la curva** | 20, 40, 60, …, 240 min (12 modelos) |
| **Subsets** | Anidados — el de N min contiene íntegramente al de N−20 min |
| **Test set** | `spk_002`, `spk_020`, `spk_024`, `spk_028` (~24 min) |
| **Validation set** | `spk_009`, `spk_029` (~15 min) |
| **Hiperparámetros** | lr=1e-3, epochs=40, batch=32, fp16, warmup=100, gradient checkpointing |
| **Decoder** | KenLM 3-grams + beam search (pyctcdecode) |
| **Métricas** | WER greedy, CER greedy, WER con LM, CER con LM |

## 📂 Estructura del repositorio

### 1️⃣ Construcción del corpus — `notebooks/create_dataset/`

Pipeline reproducible que parte de audio crudo de varias fuentes y produce el dataset publicado en el Hub.

- [`0_segment_audios.ipynb`](notebooks/create_dataset/0_segment_audios.ipynb) — segmenta el audio largo a partir de timestamps revisados.
- [`1_merge_datasets.ipynb`](notebooks/create_dataset/1_merge_datasets.ipynb) — une las sub-fuentes (YouTube, narraciones Maya Campeche, grabaciones propias) bajo un esquema común `utt_id, maya, spk_id, path`.
- [`2_transform_audio_names.ipynb`](notebooks/create_dataset/2_transform_audio_names.ipynb) — renombra audios al esquema canónico `spk_XXX_utt_YYYY.wav` y resuelve duplicados.
- [`3_explore_dataset.ipynb`](notebooks/create_dataset/3_explore_dataset.ipynb) — verifica integridad, calcula duración por hablante y total.
- [`4_load_to_hugging_face.ipynb`](notebooks/create_dataset/4_load_to_hugging_face.ipynb) — empaqueta y sube el dataset al Hub como `mau-cr/mayan-voice` (audio a 16 kHz mono, columnas `audio`, `maya`, `utt_id`, `spk_id`).
- [`correct_transcribe.ipynb`](notebooks/create_dataset/correct_transcribe.ipynb) — corrección asistida de transcripciones apoyándose en la API de Anthropic.

### 2️⃣ Análisis lingüístico y acústico

Mucho del peso del trabajo final está en las gráficas que salen de aquí:

- [`analyze_lexico.ipynb`](notebooks/create_dataset/analyze_lexico.ipynb) — distribución de palabras, n-gramas, bigramas C/V, mapas de calor de transiciones, combinaciones CV/CVC del maya.
- [`analyze_acoustic.ipynb`](notebooks/create_dataset/analyze_acoustic.ipynb) — análisis vía Praat (`parselmouth`): formantes, espacio vocálico (raw, k-means, DBSCAN), distribución de F0 por sexo, espectrogramas con formantes/intensidad.
- [`analyze_narraciones_maya_campeche.ipynb`](notebooks/create_dataset/analyze_narraciones_maya_campeche.ipynb) — análisis específico del subconjunto de Maya Campeche.
- [`mayan_statistics.ipynb`](notebooks/mayan_information/mayan_statistics.ipynb) — estadísticas sociolingüísticas sobre la población hablante, con datos del INEGI.

Las figuras renderizadas viven en [`notebooks/create_dataset/figures/`](notebooks/create_dataset/figures/).

### 3️⃣ Análisis del corpus MMS ulab v2 — `notebooks/mms_dataset/`

- [`analyze_mms.ipynb`](notebooks/mms_dataset/analyze_mms.ipynb) — exploración del corpus multilingüe no etiquetado de Meta. Justifica por qué partir de MMS-1b-all es un punto de arranque razonable para el maya.

### 4️⃣ Fine-tuning de MMS-1b-all — `notebooks/finetuning_mms_ulab_v2/`

- [`fine_tune_adapter_mms.ipynb`](notebooks/finetuning_mms_ulab_v2/fine_tune_adapter_mms.ipynb) — **notebook principal del experimento**, pensado para correr en Google Colab con GPU. Carga `mau-cr/mayan-voice`, construye splits por hablante, genera subsets anidados, entrena los doce modelos de la curva, entrena el KenLM, hace grid search de (α, β), reevalúa toda la curva con y sin LM, y empaqueta el mejor modelo + processor con LM como `mau-cr/mayan_best_model` para servirlo en una demo Gradio.

### 5️⃣ CLI `kinai` y pipeline Kaldi _(exploratorio, no activo)_

El paquete [`src/kinai/`](src/kinai/) implementa una CLI (`kinai download`, `correct`, `gen-manifest`, `gen-data`, `train`, `align`, `build-lm`, `gen-lexicon`, `segment-long`, …) que orquesta un pipeline completo de Kaldi: descarga de audio de YouTube, edición interactiva, construcción de archivos Kaldi, alineamiento forzado, entrenamiento mono/tri/tdnn/chain, lexicón y LM.

Este fue el camino inicial (replicar a Bartley & Ragni literalmente con Kaldi). El enfoque final del proyecto se movió a fine-tuning de MMS, así que muchos comandos quedan como esqueleto. Se mantiene aquí porque vertebra cómo está estructurado `corpora/` y `assets/sources/`.

### 6️⃣ Otros directorios

| Directorio | Contenido |
| --- | --- |
| [`notebooks/audio_record/`](notebooks/audio_record/) | Prototipo de interfaz para grabar audio con atajo de teclado |
| [`notebooks/dataset_information/`](notebooks/dataset_information/) | Notebooks rápidos de inspección (duración, tokens, conteos) |
| [`planning/`](planning/) | Documentos de planeación y plantilla de tesis |
| [`research/`](research/) | Papers, libros y material de referencia |
| [`tools/`](tools/) | Scripts sueltos (`align_metrics.py`, `install_kenlm.sh`, `normalize_narraciones.py`, `pad_segments.py`) |
| [`build/`](build/), [`kaldi/`](kaldi/) | Submódulo de Kaldi compilado localmente |

## 🚀 Guía rápida

### Requisitos

```bash
sudo apt update
sudo apt install portaudio19-dev ffmpeg
```

### Entorno de Python

El proyecto usa **Python ≥3.12** gestionado con [`uv`](https://github.com/astral-sh/uv) y `pyproject.toml`:

```bash
uv sync
```

Esto instala las dependencias declaradas en [`pyproject.toml`](pyproject.toml) (datasets, librosa, parselmouth, transformers, matplotlib, scienceplots, typer, yt-dlp, etc.) y expone el comando `kinai`.

### Fine-tuning en Colab

El notebook de fine-tuning está pensado para Google Colab con GPU. La primera celda instala todo lo necesario:

```python
!pip install -q -U "datasets[audio]==3.6.0" "huggingface_hub" "soundfile" \
    "librosa" "evaluate" "jiwer" "accelerate" \
    "transformers @ git+https://github.com/huggingface/transformers.git"
!pip install -q https://github.com/kpu/kenlm/archive/master.zip
!pip install pyctcdecode
```

### Inferencia rápida con el mejor modelo

```python
from transformers import AutoProcessor, AutoModelForCTC
import librosa, torch

processor = AutoProcessor.from_pretrained("mau-cr/mayan_best_model")
model = AutoModelForCTC.from_pretrained("mau-cr/mayan_best_model").eval()

señal, _ = librosa.load("ejemplo.wav", sr=16000, mono=True)
inputs = processor(señal, sampling_rate=16000, return_tensors="pt")

with torch.no_grad():
    logits = model(**inputs).logits

print(processor.batch_decode(logits.cpu().numpy()).text[0])
```

## 🛠️ Tech Stack

### 🎙️ Speech & ML

- **[MMS-1b-all](https://huggingface.co/facebook/mms-1b-all)** — Modelo acústico multilingüe preentrenado de Meta
- **[Transformers](https://huggingface.co/docs/transformers)** — Framework para fine-tuning y manejo del processor
- **[PyTorch](https://pytorch.org/)** — Backend de cómputo (fp16, gradient checkpointing)
- **[KenLM](https://github.com/kpu/kenlm)** — Modelo de lenguaje n-gram (3-gramas en este proyecto)
- **[pyctcdecode](https://github.com/kensho-technologies/pyctcdecode)** — Decoder de beam search con LM
- **[datasets](https://huggingface.co/docs/datasets)** — Manejo del corpus, splits por hablante, subsets anidados
- **[evaluate](https://huggingface.co/docs/evaluate) + [jiwer](https://github.com/jitsi/jiwer)** — Cálculo de WER/CER

### 🎵 Audio & Phonetics

- **[librosa](https://librosa.org/)** + **[soundfile](https://pysoundfile.readthedocs.io/)** — Carga, resampling, manipulación de audio
- **[Parselmouth (Praat)](https://parselmouth.readthedocs.io/)** — Análisis fonético: formantes, F0, intensidad
- **[Kaldi](https://kaldi-asr.org/)** — Pipeline clásico (exploratorio, no activo)

### 🌐 Interfaces y herramientas

- **[Gradio](https://gradio.app/)** — Demo interactiva sobre Hugging Face Spaces
- **[Hugging Face Hub](https://huggingface.co/)** — Hosting de modelos, dataset y Space
- **[Typer](https://typer.tiangolo.com/)** — CLI `kinai`
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — Descarga de audio de YouTube
- **[uv](https://github.com/astral-sh/uv)** — Gestor de entorno y dependencias

### 📊 Visualización y Análisis

- **[matplotlib](https://matplotlib.org/)** + **[scienceplots](https://github.com/garrettj403/SciencePlots)** — Gráficas científicas
- **[scikit-learn](https://scikit-learn.org/)** — k-means y DBSCAN para clustering del espacio vocálico
- **[pandas](https://pandas.pydata.org/)** + **[numpy](https://numpy.org/)** — Manipulación de datos y métricas

## 🤖 Uso de Inteligencia Artificial

Este proyecto utilizó herramientas de IA en varias etapas del desarrollo:

- **Claude (Anthropic)** — Corrección asistida de transcripciones, diseño del pipeline de fine-tuning, debugging y redacción técnica
- **Claude Code** — Generación de scripts, estructuración del repositorio y documentación
- **Modelos preentrenados de Meta (MMS)** — Backbone del sistema ASR

## 📋 Status & Trabajo Pendiente

Este repositorio **no está terminado**. Lo que sigue abierto:

- [ ] Publicar el Space de Gradio público
- [ ] Limpiar/archivar o actualizar el pipeline Kaldi que ya no se usa
- [ ] Análisis cualitativo de errores frecuentes del modelo (sustituciones, inserciones, eliminaciones)

## 📚 Referencias Clave

- Bartley, C. & Ragni, A. (2025). _How I Built ASR for Endangered Languages with a Spoken Dictionary_. [arXiv:2510.04832](https://arxiv.org/abs/2510.04832)
- Mainzinger, J. & Levow, G.-A. (2024). _Fine-tuning multilingual pretrained models for Mvskoke ASR_.
- Romero, M., Gómez-Canaval, S. & Torre, I. G. (2024). _Automatic Speech Recognition Advancements for Indigenous Languages of the Americas_. Applied Sciences, 14(15), 6497.
- Pratap, V. et al. (2023). _Scaling Speech Technology to 1,000+ Languages_. (Introduce MMS y MMS ulab.)

---

<div align="center">

**🪶 Maya yucateco · ASR · Tesis en desarrollo · Mérida, Yucatán**

</div>