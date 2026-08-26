# `tools/` — dependencias externas

Nada de aquí se versiona: son compilaciones locales, pesadas y reproducibles con los
scripts de esta misma carpeta.

| Carpeta | Qué es | Cómo se obtiene |
| --- | --- | --- |
| `kaldi/` | clon de [kaldi-asr/kaldi](https://github.com/kaldi-asr/kaldi) ya compilado (~9,7 G) | `install_kaldi.sh` — **pendiente de escribir**; hoy hay que seguir el `INSTALL` de Kaldi a mano |
| `kenlm/` | [KenLM](https://github.com/kpu/kenlm) compilado, para `lmplz` / `build_binary` | `./install_kenlm.sh` |

`install_system_deps.sh` instala lo que necesita el sistema (portaudio, python3-tk) y
Node vía nvm para `projects/speech-collector/`.

La receta archivada de Kaldi (`projects/kaldi_asr/recipe/`) apunta aquí con enlaces
simbólicos **relativos**, así que funciona esté donde esté clonado el repo:

```bash
cd projects/kaldi_asr/recipe && . ./path.sh && which compute-mfcc-feats
```
