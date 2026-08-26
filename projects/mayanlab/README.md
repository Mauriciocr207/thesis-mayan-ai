# `mayanlab` — infraestructura compartida

Paquete instalable con lo que usan todos los demás proyectos.

## `mayanlab.paths`

La **única** definición de rutas del repositorio. Ningún notebook ni script tiene rutas
propias, así que ninguno depende del directorio desde el que se ejecute.

```python
from mayanlab.paths import AUDIO, ANNOTATIONS, MANIFESTS, TRANSCRIPTS, project

df = pd.read_csv(MANIFESTS / "dataset.csv")
wav = AUDIO / f"{utt_id}.wav"
plt.savefig(project("analysis").figures / "vowel_space.svg")
```

La raíz de datos es `<repo>/data` salvo que se defina `MAYAN_DATA` (en `.env` o en el
entorno), lo que permite moverla a otro disco o, en Colab, a Drive:

```python
import os
os.environ["MAYAN_DATA"] = "/content/drive/MyDrive/thesis-mayan-ai/data"
from mayanlab.paths import AUDIO   # ya apunta a Drive
```

`project("nombre")` da las carpetas de un proyecto: `.notebooks`, `.scripts`, `.figures`,
`.features`, `.data`, `.results`. `ensure(*paths)` crea las que falten.

## `mayanlab.tokenizer`

Tokenizador fonémico del maya yucateco: `MayaPhonemeTokenizer`, `IPA_TO_KALDI`,
`modernize_orthography`, `normalize_word`. Lo usan los notebooks de análisis y el pipeline
archivado de Kaldi.
