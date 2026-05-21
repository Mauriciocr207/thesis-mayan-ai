# CHECKLIST HORA-A-HORA: 48 HORAS PARA TERMINAR

## DÍA 1: ENTRENAMIENTO + ALINEACIÓN

### MAÑANA (8:00 - 12:00)
**Objetivo:** Empezar entrenamientos que corran en background

```bash
# 8:00 - Prepara datos
# Asegúrate que tienes:
ls -la data/train/feats.scp       # Features deben existir
ls -la data/train/text            # Transcripciones en formato: spk_XXX frase
ls -la data/test/feats.scp        # Test set separado

# 8:15 - INICIA ENTRENAMIENTO
# Este proceso tarda ~2-3 horas, corre en background
nohup bash 01_train_iter2.sh > train.log 2>&1 &
tail -f train.log  # Monitorea en otra terminal

# 8:30 - Mientras entrena, EMPIEZA A ESCRIBIR
# Abre tu documento de tesis
# Copia Introducción del protocolo (cambiar mínimamente)
# Copia Marco Teórico del protocolo (cambiar mínimamente)
# Adapta Metodología a lo que REALMENTE hiciste
```

**Mientras esperas (8:30 - 12:00):** Escribe Introducción + Marco Teórico + Metodología
- Esto debería tomar 3-4 horas, perfecto para el tiempo de entrenamiento
- SI TERMINAS ANTES: crea las tablas vacías de resultados en tu documento

### ALMUERZO Y DESCANSO (12:00 - 13:00)

### TARDE (13:00 - 18:00)
**Objetivo:** Decodificación sin LM y comenzar LM

```bash
# 13:00 - Verifica que el entrenamiento terminó
# En otra terminal:
tail -20 train.log
ls -la exp/tri1_iter2/final.mdl  # Debe existir este archivo

# 13:30 - DECODIFICA SIN LM
bash 02_decode_noLM.sh > decode.log 2>&1
# Esto tarda ~20 minutos

# 13:50 - Mientras decodifica, EMPIEZA MODELO DE LENGUAJE
bash 03_build_lm.sh > lm.log 2>&1 &

# 14:00 - Verifica WER sin LM
tail -20 decode.log
grep "Overall" exp/tri1_iter2/wer_noLM.txt
# ANOTA ESTE NÚMERO: será WER_FINAL_NO_LM = XX.XX%

# 14:15 - Escribe Sección 4.1 y 4.2.1 de tesis
# (Estadísticas del corpus + WER sin LM)
# Usa la PLANTILLA_TESIS.md
```

**14:30 - 18:00:** Escribe secciones de resultados iniciales

### NOCHE (18:00 - 24:00)
**Objetivo:** Alineación + análisis + MÁS escritura

```bash
# 18:00 - Verifica que LM está listo
ls -la exp/lm/lm.fst  # Debe existir

# 18:30 - DECODIFICA CON LM
bash 04_decode_with_lm.sh > decode_lm.log 2>&1

# 18:45 - Mientras decodifica, ANALISIS DE ALINEACION
# Abre Praat
# Selecciona 3-5 audios de test
# Alinea manualmente 1-2 minutos de audio como referencia

# 19:00 - Verifica WER con LM
grep "Overall" exp/tri1_iter2/wer_withLM.txt
# ANOTA ESTE NÚMERO: será WER_FINAL_CON_LM = YY.YY%

# 19:30 - GENERA METRICAS
python3 generate_metrics.py
# Esto crea metrics_summary.md y metrics.json

# 20:00 - Calcula diferencias
# Manual: WER_NOLM - WER_CONLM = mejora
# Escríbelo en tu documento

# 20:30 - 23:59: ESCRIBE SECCIONES 4.2.2 (con LM), 4.3 (alineación)
# Usa PLANTILLA_TESIS.md
```

---

## DÍA 2: ANÁLISIS FINAL + ESCRITURA

### MAÑANA (8:00 - 12:00)
**Objetivo:** Análisis acústico + finalizar secciones de resultados

```bash
# 8:00 - ANÁLISIS ACUSTICO
# Si tienes tiempo: corre script de Parselmouth
# SI NO TIENES TIEMPO: SALTA ESTO

python3 << 'EOF'
import parselmouth
import numpy as np
from pathlib import Path

# Rápidamente extrae F0 y formantes de 5 archivos test
test_files = list(Path("data/test").glob("*.wav"))[:5]

f0_values = []
for audio_file in test_files:
    sound = parselmouth.Sound(str(audio_file))
    pitch = parselmouth.praat.call(sound, "To Pitch", 0.0, 75, 300)
    f0 = parselmouth.praat.call(pitch, "Get mean", 0, 0)
    f0_values.append(f0)

print(f"F0 promedio: {np.mean(f0_values):.1f} Hz")
print(f"F0 rango: {np.min(f0_values):.1f} - {np.max(f0_values):.1f} Hz")
EOF

# Resultado → ponlo en tu documento
```

**8:30 - 12:00:** Escribe Secciones 4.4 (cobertura fonética) + 4.5 (características acústicas)

### ALMUERZO (12:00 - 13:00)

### TARDE (13:00 - 18:00)
**Objetivo:** Discusión + Conclusiones + Revisión

```bash
# 13:00 - Abre tu documento

# 13:00 - 15:00: Escribe Sección 5 (DISCUSIÓN)
# Plantilla está en PLANTILLA_TESIS.md
# Responde: ¿Qué significan mis números?
# Compara con Bartley et al.

# 15:00 - 16:30: Escribe Sección 6 (CONCLUSIONES)
# - Qué lograste
# - Limitaciones (sé honesto)
# - Trabajo futuro

# 16:30 - 17:00: Resumen ejecutivo
# 1 página que explique todo el proyecto
```

### NOCHE (18:00 - 22:00)
**Objetivo:** Revisión final + ajustes

```bash
# 18:00 - 20:00: REVISION COMPLETA
# Lee el documento de principio a fin
# Busca:
#   ☐ Errores ortográficos
#   ☐ Referencias correctas [1], [2], etc.
#   ☐ Tablas con números correctos
#   ☐ Gráficos legibles
#   ☐ Párrafos no muy robóticos

# 20:00 - 21:00: AJUSTES DE FORMATO
# - Márgenes correctos
# - Numeración de páginas
# - Portada con información correcta
# - Tabla de contenidos actualizada

# 21:00 - 22:00: EXPORTA A PDF
# Asegúrate que el PDF se ve bien
# Verifica: fuentes, espacios, imágenes

# 22:00: ENTREGA
```

---

## PLANTILLA MINIMA DE TABLA QUE NECESITAS

Copia esto en tu documento Y RELLENA LOS NUMEROS:

### Tabla 4.2.1: WER sin Modelo de Lenguaje
| Configuración | Duración | WER | Mejora |
|---|---|---|---|
| Baseline (7 min, monophone) | 7 min | XX.XX% | - |
| Baseline (7 min, triphone) | 7 min | XX.XX% | -Y.YY% |
| **Final (50 min, triphone)** | 50 min | **ZZ.ZZ%** | **-WW.WW%** |

### Tabla 4.2.2: Efecto del Modelo de Lenguaje
| Modelo | Sin LM | Con LM | Ganancia |
|---|---|---|---|
| Final (50 min) | ZZ.ZZ% | AA.AA% | -BB.BB% |

---

## NUMEROS CLAVE QUE NECESITAS ANOTAR

**Día 1 tarde:**
- [ ] WER sin LM: _____%

**Día 1 noche:**
- [ ] WER con LM: _____%
- [ ] Mejora con LM: _____%

**Día 2 mañana:**
- [ ] F0 promedio: _____ Hz
- [ ] Fonemas bien alineados: _____%

---

## SEÑALES DE ALERTA

**Si ves esto, DETENTE y revisa:**

❌ WER > 70% → Algo está muy mal en Kaldi, revisar features
❌ WER mejora < 2% con LM → LM no se entrenó bien
❌ WER NO mejora de iter 1 a iter 2 → Datos nuevos no ayudaron (ok, documenta esto)
❌ Alineaciones con error > 200 ms → Manuales tus datos, hay ruido
❌ Test set WER mucho > train set WER → Overfitting

**Si pasa algo de esto:** No entraes en pánico. Documéntalo honestamente en la tesis: "Esperaba X pero obtuve Y porque Z". Eso es válido.

---

## COMANDOS RAPIDOS DE DEBUG

```bash
# ¿Cuántos archivos alineó?
grep "Aligning" train.log | wc -l

# ¿Cuál fue el error de entrenamiento al final?
tail -50 tri1_iter2.log | grep "Overall"

# ¿El modelo acústico es válido?
ls -lh exp/tri1_iter2/final.mdl

# ¿Decode terminó?
wc -l exp/tri1_iter2/decode_test_noLM/one-best.tra

# ¿Cuántas palabras en el LM?
grep "1-grams:" exp/lm/lm.arpa -A 5 | wc -l
```

---

## SI TE QUEDAS SIN TIEMPO

**Prioridad 1 (NO SALTES ESTO):**
- Tesis con números de WER
- Tabla comparativa

**Prioridad 2 (Si puedes):**
- Análisis de alineación

**Prioridad 3 (Nice-to-have):**
- Análisis acústico detallado

**NUNCA saltes la escritura.** Sin tesis, los números no valen nada.

---

## CUANDO TERMINES

1. Copia tesis a USB/nube
2. Copia scripts a USB/nube (como apéndice?)
3. Copia métricas (metrics_summary.md, metrics.json)
4. RESPIRA - lo lograste 🎉

