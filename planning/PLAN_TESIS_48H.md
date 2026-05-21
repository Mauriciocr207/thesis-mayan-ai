# Plan de Ejecución: Tesis en 48 Horas
## Carillo - Corpus Maya Yucateco + ASR/Kaldi

---

## RESUMEN EJECUTIVO
**Objetivo realista:** Demostrar que pasaste de un modelo débil (7 min) a uno más robusto (~50 min total) con mejoras medibles en alineación y WER, validando el enfoque iterativo.

**NO es objetivo:** Conseguir un ASR perfecto. Es demostrar methodology + datos + comparativa.

---

## DÍA 1: ENTRENAMIENTO + LÍNEA BASE (Horas 0-24)

### Bloque 1: Preparación rápida (2 horas)
**Ahora mismo (mañana temprano):**

1. **Organiza tus datos nuevos** (30 min)
   - Coloca los ~43 minutos nuevos de audio en estructura Kaldi
   - Nombre estándar: `spk_XXX_utt_YYYY.wav` + `spk_XXX_utt_YYYY.txt`
   - Crea `data/train/wav.scp`, `data/train/text`, etc.

2. **Crea un test set limpio** (1.5 horas)
   - **CRUCIAL:** Toma 5-7 minutos de audio (mejor de diferentes hablantes que tus datos de entrenamiento si es posible)
   - Si no tienes otro hablante, toma las últimas frases que grabaste
   - Nómbralo `data/test/`
   - Esto es inviolable: **nunca entrenes con test**

### Bloque 2: Bootstrapping del modelo (3 horas)
**Estrategia:** Usa tu modelo de 7 minutos como punto de partida

```bash
# Tu modelo de 7 min ya está en exp/mono/final.mdl (o triphone)
# Ahora vas a:

1. Alinea los datos NUEVOS (43 min) con el modelo viejo
   align-equal-compiled exp/mono/final.mdl scp:data/train/feats.scp \
     ark:data/train/text ark,t:ali.txt

2. Combina las alineaciones: viejo (7 min) + nuevo (43 min)

3. Re-entrena monophone con TODOS (50 min)
   - Esto es rápido (~30 min de CPU)
   - Guarda como exp/mono_iter2/

4. Re-entrena triphone con TODOS (esto tardará ~1.5 horas)
   - Guarda como exp/tri1_iter2/
```

**Por qué esto funciona:** Es mucho más rápido que entrenar desde cero, y típicamente ves mejoras claras porque tu modelo inicial, aunque débil, tenía la estructura correcta.

### Bloque 3: Evaluación rápida (1.5 horas)
**Decoding sin modelo de lenguaje (para tener baseline)**

```bash
# Decodifica con triphone iter2
decode exp/tri1_iter2/graph \
  data/test/feats.scp ark,t:result.txt

# Calcula WER contra referencia
compute-wer --text ark:data/test/text ark,t:result.txt > wer_sin_lm.txt
```

**Qué esperar:** 
- Sin LM: probablemente 40-60% WER (está bien, es esperado)
- Anota el número exacto, lo vas a usar en la tesis

**Salida de esta fase:**
- `wer_sin_lm.txt` → métrica clave
- Tablas de confusión de fonemas (córtelas con scripts Python rápidos)

---

## DÍA 2: MODELO DE LENGUAJE + RESULTADOS FINALES (Horas 24-48)

### Bloque 4: Modelo de Lenguaje simple (3 horas)

**Estrategia:** NO hagas un LM sofisticado. Usa lo que tienes.

```bash
# Opción A (RECOMENDADO - 30 min):
# Construye un n-grama de 3 con SRILM o el que uses

cat data/train/text | awk '{$1=""; print}' > words.txt
# Entrena LM trigrama
ngram-count -text words.txt -lm lm.arpa -interpolate -kndiscount -order 3

# Opción B (si no tienes SRILM disponible - 15 min):
# Usa el script de Kaldi
local/format_lm.sh data/lang_test data/train/text \
  exp/lm/lm.arpa exp/lm/lm.fst
```

**Por qué así:**
- Trigrama es suficiente para tu corpus pequeño
- No necesitas texto externo (evita distracciones)
- Tarda poco

### Bloque 5: Decodificación CON LM (2 horas)

```bash
# Re-decodifica con LM
decode_with_lm exp/tri1_iter2/graph_lm \
  data/test/feats.scp ark,t:result_con_lm.txt

# Calcula WER
compute-wer --text ark:data/test/text ark,t:result_con_lm.txt > wer_con_lm.txt
```

**Qué esperar:**
- Mejora de 5-15 puntos en WER (típico)
- Esto es lo que mostrarás como "beneficio del LM"

### Bloque 6: Métricas de alineación (2 horas)

**Esto es VISUAL y CUANTITATIVO para tu tesis:**

```bash
# Compara alineaciones: modelo inicial vs final

# 1. Toma 3-5 audios al azar de tu test set
# 2. Para cada uno:

# A. Alinea con modelo viejo (7 min)
ali-to-ctm --frame-shift=0.01 \
  exp/mono/final.mdl ali.txt ali_old.ctm

# B. Alinea con modelo nuevo (50 min)
ali-to-ctm --frame-shift=0.01 \
  exp/tri1_iter2/final.mdl ali.txt ali_new.ctm

# C. Compara manualmente en Praat o calcula diferencias
# (escribe script Python para medir diferencias en ms)
```

**Qué medir específicamente:**

```python
# Script Python rápido (máximo 30 min escribirlo)
import numpy as np

# Carga ali_old.ctm y ali_new.ctm
# Para cada fonema en cada utterance, calcula:
# - Diferencia en tiempo de inicio (ms)
# - Diferencia en duración (ms)

diffs = []
for line_old, line_new in zip(old_alignment, new_alignment):
    if line_old['phoneme'] == line_new['phoneme']:
        diff = abs(line_old['start_time'] - line_new['start_time']) * 1000
        diffs.append(diff)

mean_diff = np.mean(diffs)
std_diff = np.std(diffs)
print(f"Error promedio: {mean_diff:.1f} ms ± {std_diff:.1f} ms")
```

**Salida esperada:**
- Documento con tabla: "Precisión de alineación mejoró de X ms a Y ms"

### Bloque 7: Análisis acústico rápido (1.5 horas)

**NO hagas análisis exhaustivo. Haz 2-3 cosas concretas:**

```python
# Script Python con Parselmouth (ya sabes usarlo)

import parselmouth
import numpy as np

# Para tus datos de test:
# 1. Extrae F0 de vocales
# 2. Calcula duración promedio por fonema
# 3. Extrae primer MFCC

results = {
    'fonema': [],
    'f0_promedio': [],
    'duracion_ms': [],
    'mfcc_1': []
}

# Procesa 5-10 archivos de test
for audio_file in test_files[:10]:
    sound = parselmouth.Sound(audio_file)
    # ... análisis básico
    
# Crea tabla resumen para la tesis
```

**Qué reportar:**
- Tabla: "Características acústicas del corpus final"
- 1 gráfico: distribución de F0 por género
- 1 gráfico: duración de vocales vs consonantes

---

## SIMULTANEO CON TODO: ESCRITURA DE TESIS (distribúyelo)

**No esperes al final.** Escribe mientras avanza el trabajo.

### Estructura que deberías tener ANTES de día 2:

```
Sección ya escrita:
✓ 1. Introducción (usa la tuya del protocolo, 80% igual)
✓ 2. Marco teórico (COPEA del protocolo, es sólido)
✓ 3. Metodología (adapta protocolo a lo real que hiciste)
  - Cita el protocolo pero especifica lo que realmente pasó
  
Escribe día 1 tarde:
□ 4. Resultados
  - 4.1 Estadísticas del corpus
  - 4.2 WER sin LM
  - 4.3 WER con LM
  - 4.4 Análisis de alineación
  - 4.5 Características acústicas

Escribe día 2:
□ 5. Discusión (¿qué significa esto?)
□ 6. Conclusiones
□ Resumen ejecutivo
```

### Tabla clave que necesitas (prepárala YA):

```
| Métrica | Modelo Inicial (7 min) | Modelo Final (50 min) | Mejora |
|---------|----------------------|----------------------|--------|
| WER (sin LM) | XX% | YY% | -Z% |
| WER (con LM) | XX% | YY% | -Z% |
| Cobertura de fonemas | ?/? | ?/? | +? |
| Error alineación (ms) | ±A ms | ±B ms | -C ms |
| Utterances alineados | XX% | YY% | +Z% |
```

**Esto resume TODO tu trabajo en una tabla.**

---

## CRONOGRAMA REALISTA

### DÍA 1
- **8:00-8:30:** Preparación datos (30 min)
- **8:30-12:00:** Entrenamiento monophone + triphone iter2 (mientras, ESCRIBE introducción)
- **12:00-13:00:** Almuerzo + descanso
- **13:00-14:30:** Decodificación sin LM + WER
- **14:30-18:00:** Escribe metodología + resultados parciales
- **18:00-20:00:** Alineación comparativa (Bloque 6)
- **20:00-21:30:** Análisis acústico rápido
- **21:30-23:59:** Escribe más resultados, prepara gráficos

### DÍA 2
- **8:00-11:00:** Modelo de lenguaje + decodificación con LM
- **11:00-12:00:** Cálculo WER con LM
- **12:00-13:00:** Escribe resultados finales
- **13:00-14:00:** Prepara gráficos/tablas
- **14:00-18:00:** Escribe discusión y conclusiones
- **18:00-20:00:** Revisión completa de documento
- **20:00-21:00:** Ajustes finales

---

## LO QUE NO HAGAS (ahorrar tiempo)

❌ No intentes tuning fino de hyperparameters  
❌ No hagas análisis de formantes detallado (solo promedio)  
❌ No construyas un LM sofisticado  
❌ No intentes mejorar más allá de triphone  
❌ No compares contra baseline complejos  

---

## LO QUE SÍ DEBES HACER

✅ Documentar CLARAMENTE lo que pasó  
✅ Mostrar números concretos (WER, alineación, cobertura)  
✅ Explicar por qué esperabas esos números  
✅ Ser honesto si algo falló ("esperaba X pero obtuve Y porque...")  
✅ Conectar resultados con la pregunta de investigación  

---

## PREGUNTA CENTRAL DE TU TESIS

Deberías poder responder esto en 1 página:

**"¿Qué tan robusto es pasar de 7 minutos a 50 minutos de audio para crear un corpus alineado fonéticamente en maya yucateco que pueda servir como base para ASR?"**

**Respuesta esperada:**
- Con 7 min: modelo débil, muchos errores de alineación, cobertura fonética incompleta
- Con 50 min: modelo más estable, menos errores de alineación, mejor cobertura
- Mejora en WER de X a Y puntos
- Esto demuestra que el enfoque iterativo (pequeño → grande) es viable

---

## ARCHIVOS QUE NECESITAS AL FINAL

1. `wer_sin_lm.txt` - métrica clave
2. `wer_con_lm.txt` - métrica clave
3. `alignment_comparison.txt` - tabla de comparación
4. `acoustic_summary.csv` - características del corpus
5. Script de Python que generó (2), (3), (4)
6. Documento de tesis (PDF/DOCX)

---

## SI TE QUEDAS SIN TIEMPO...

**Prioridades en orden:**
1. Tesis escrita (sin esto, nada sirve)
2. WER con y sin LM (esto es lo visual de tu trabajo)
3. Tabla comparativa (resumen ejecutivo)
4. Análisis acústico (si sobra tiempo)

Si solo tienes 1.5 días: **salta análisis acústico detallado, mantén el resto.**

---

## NOTAS FINALES

- Tu protocolo es sólido, reutilízalo
- Bartley demostró que con poco dato y Kaldi se puede, tú estás replicando eso
- La historia que cuentas es: "partí con 7 min, sabía que era poco, recogí más, reentrené, mejoré X"
- Eso **es** válido para una tesis
- Los números importan, pero la claridad importa más

**Buena suerte. Enfócate, no perfecciones.**
