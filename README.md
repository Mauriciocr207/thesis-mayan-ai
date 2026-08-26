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

**thesis-mayan-ai** es el repositorio de mi tesis sobre **reconocimiento automático del habla
(ASR) en maya yucateco**. Reúne dos líneas de trabajo que se sostienen mutuamente: la
construcción y análisis de un **corpus propio** de ~4 horas de audio etiquetado, y el **ajuste
fino de [MMS-1b-all](https://huggingface.co/facebook/mms-1b-all)** sobre ese corpus para trazar
una curva de aprendizaje que responda la pregunta de fondo: ¿cuánto audio necesita el maya
yucateco para un ASR usable?

> 📚 **Pregunta de investigación**: la lógica experimental replica a
> [Bartley y Ragni (2025)](https://arxiv.org/abs/2510.04832), quienes mostraron que con apenas
> 40 minutos de audio bien curado se puede entrenar un ASR funcional para lenguas críticamente
> en peligro. Aquí se explora un **modelo preentrenado moderno** ajustado vía **adapters de
> lengua** sobre el código ISO `yua`.

## 🔗 Recursos

| Recurso | Ubicación |
| --- | --- |
| 🎙️ **Corpus** | [`mau-cr/mayan-voice`](https://huggingface.co/datasets/mau-cr/mayan-voice) |
| 📊 **Modelos por punto de curva** | `mau-cr/mms-maya-020min` … [`mau-cr/mms-maya-240min`](https://huggingface.co/mau-cr/mms-maya-240min) |
| 🏆 **Mejor modelo (240 min + LM)** | [`mau-cr/mayan_best_model`](https://huggingface.co/mau-cr/mayan_best_model) |
| 📈 **Resultados de scaling** | [`mau-cr/mms_yua_results`](https://huggingface.co/datasets/mau-cr/mms_yua_results) |
| 📄 **Paper de referencia** | [Bartley & Ragni, 2025](https://arxiv.org/abs/2510.04832) |

## 📂 Cómo está organizado

Dos ideas: **`data/` es la única raíz de datos** y **`projects/` contiene los proyectos**.

```
thesis-mayan-ai/
├── data/          ── TODOS los datos, source → work → final   (ver data/README.md)
├── projects/
│   ├── corpus/         ACTIVO    construcción del dataset
│   ├── analysis/       ACTIVO    análisis lingüístico y acústico
│   ├── mms_asr/        ACTIVO    fine-tuning de MMS (Colab)
│   ├── mayanlab/       paquete   rutas compartidas + tokenizador fonémico
│   ├── ytclip/         paquete   descarga y recorte de audio (CLI `ytclip`)
│   ├── speech-collector/         app de recolección de grabaciones (fork, sin uso activo)
│   └── kaldi_asr/      ARCHIVADO el primer pipeline, con Kaldi
├── tools/         ── dependencias externas compiladas: kaldi/, kenlm/
└── research/      ── material académico (no versionado)
```

Cada proyecto tiene su `README.md` con lo que hace, qué está pendiente y cómo ejecutarlo.

### Una sola definición de rutas

Ningún notebook ni script tiene rutas relativas: todos importan de `mayanlab.paths`, así que
funcionan desde cualquier directorio.

```python
from mayanlab.paths import AUDIO, ANNOTATIONS, MANIFESTS, TRANSCRIPTS, project

df  = pd.read_csv(MANIFESTS / "dataset.csv")
wav = AUDIO / f"{utt_id}.wav"
plt.savefig(project("analysis").figures / "vowel_space.svg")
```

Los datos viven en `<repo>/data` salvo que definas `MAYAN_DATA` en `.env`, lo que los mueve a
otro disco —o a Drive en Colab— sin tocar una sola celda.

## 🚀 Guía rápida

```bash
sudo apt install portaudio19-dev ffmpeg     # o: ./tools/install_system_deps.sh
uv sync                                     # entorno + paquetes mayanlab y ytclip
cp .env.example .env                        # MAYAN_DATA (opcional), ANTHROPIC_API_KEY

uv run ytclip where                         # comprueba dónde resuelven las rutas
```

### Reproducir el corpus

```bash
# 1. Las transcripciones alineadas del subcorpus de 3 h
uv run python projects/corpus/scripts/build_3h_transcripts.py --check

# 2. El resto del pipeline, en projects/corpus/notebooks/, en orden:
#    00a → 00c (narraciones del INALI) · 0 → 4 (segmentar, unir, renombrar, publicar)
#    5_how_to_dataset.ipynb genera el manifiesto de procedencia
```

### Inferencia con el mejor modelo

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

## 🧠 Metodología

### El punto de partida: MMS ulab v2 y MMS-1b-all

**MMS ulab v2** es el corpus multilingüe no etiquetado que Meta construyó dentro de _Scaling
Speech Technology to 1000+ Languages_: ~8.900 horas en 4.023 lenguas, el maya yucateco entre
ellas. Una porción sirvió para preentrenar la familia **MMS**, lo que vuelve a MMS-1b-all un
punto de partida natural: aunque nunca haya visto transcripciones en maya, ya tiene
representaciones internas razonables para sus sonidos.

### Ajuste fino con adapters

En lugar de actualizar los miles de millones de parámetros del modelo base, el entrenamiento
**congela toda la base preentrenada** y solo ajusta los adapters de la lengua objetivo
(`target_lang="yua"`), la estrategia que Mainzinger y Levow (2024) reportan como la más
adecuada para lenguas de bajos recursos:

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
| **Subsets** | Anidados — el de N min contiene íntegramente al de N−20 |
| **Test set** | `spk_002`, `spk_020`, `spk_024`, `spk_028` (~24 min) |
| **Validación** | `spk_009`, `spk_029` (~15 min) |
| **Hiperparámetros** | lr=1e-3, epochs=40, batch=32, fp16, warmup=100, gradient checkpointing |
| **Decoder** | KenLM 3-gramas + beam search (pyctcdecode) |
| **Métricas** | WER y CER, greedy y con LM |

## 🎯 Principales características

- **🎙️ Corpus propio** — 2.535 utterances de 32 hablantes, ~4 horas, mono 16 kHz, de tres
  fuentes: YouTube didáctico, Narraciones Mayas de Campeche (INALI) y grabaciones propias.
- **📈 Curva de aprendizaje completa** — doce modelos con la misma semilla y subsets anidados,
  para que la única variable sea la cantidad de audio.
- **🧩 Fine-tuning con adapters** — backbone congelado, coste computacional razonable.
- **🔤 Decodificación con LM** — KenLM de 3-gramas + beam search, con grid search de (α, β).
- **👥 Splits por hablante** — test y validación con hablantes hold-out fijos.
- **📊 Análisis lingüístico y acústico** — espacio vocálico, formantes, F0, n-gramas, mapas de
  calor CV/CVC, todo reproducible desde `projects/analysis/`.

## 🛠️ Tech Stack

**Speech & ML** · [MMS-1b-all](https://huggingface.co/facebook/mms-1b-all) ·
[Transformers](https://huggingface.co/docs/transformers) · [PyTorch](https://pytorch.org/) ·
[KenLM](https://github.com/kpu/kenlm) ·
[pyctcdecode](https://github.com/kensho-technologies/pyctcdecode) ·
[datasets](https://huggingface.co/docs/datasets) · [jiwer](https://github.com/jitsi/jiwer)

**Audio & fonética** · [librosa](https://librosa.org/) ·
[soundfile](https://pysoundfile.readthedocs.io/) ·
[Parselmouth (Praat)](https://parselmouth.readthedocs.io/) ·
[Kaldi](https://kaldi-asr.org/) _(archivado)_

**Herramientas** · [Typer](https://typer.tiangolo.com/) ·
[yt-dlp](https://github.com/yt-dlp/yt-dlp) · [uv](https://github.com/astral-sh/uv) ·
[Hugging Face Hub](https://huggingface.co/) · [Gradio](https://gradio.app/)

**Visualización** · [matplotlib](https://matplotlib.org/) +
[scienceplots](https://github.com/garrettj403/SciencePlots) ·
[scikit-learn](https://scikit-learn.org/) · [pandas](https://pandas.pydata.org/)

## 🤖 Uso de Inteligencia Artificial

- **Claude (Anthropic)** — corrección asistida de transcripciones, diseño del pipeline de
  fine-tuning, debugging y redacción técnica
- **Claude Code** — generación de scripts, estructuración del repositorio y documentación
- **Modelos preentrenados de Meta (MMS)** — backbone del sistema ASR

## 📋 Status y trabajo pendiente

- [ ] **Adaptar el lector del manifiesto** al formato de tres grupos para que `ytclip download`
      reconstruya el corpus desde un clon limpio — ver
      [`projects/ytclip/README.md`](projects/ytclip/README.md)
- [ ] Decidir cómo se publican las 100 grabaciones propias, hoy sin versionar
- [ ] Revisar `spk_002_utt_0124` / `spk_002_utt_0125`: son el mismo audio byte a byte en el
      dataset publicado
- [ ] Publicar el Space de Gradio
- [ ] Completar `tools/install_kaldi.sh`
- [ ] Análisis cualitativo de errores del modelo (sustituciones, inserciones, eliminaciones)

## 📚 Referencias clave

- Bartley, C. & Ragni, A. (2025). _How I Built ASR for Endangered Languages with a Spoken
  Dictionary_. [arXiv:2510.04832](https://arxiv.org/abs/2510.04832)
- Mainzinger, J. & Levow, G.-A. (2024). _Fine-tuning multilingual pretrained models for Mvskoke
  ASR_.
- Romero, M., Gómez-Canaval, S. & Torre, I. G. (2024). _Automatic Speech Recognition Advancements
  for Indigenous Languages of the Americas_. Applied Sciences, 14(15), 6497.
- Pratap, V. et al. (2023). _Scaling Speech Technology to 1,000+ Languages_.

---

<div align="center">

**🪶 Maya yucateco · ASR · Tesis en desarrollo · Mérida, Yucatán**

</div>
