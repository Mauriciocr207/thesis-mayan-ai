#!/bin/bash
# Script 1: PREPARACION Y ENTRENAMIENTO RAPIDO
# Úsalo así: bash train_iter2.sh

# Configuración
KALDI_ROOT=/path/to/kaldi  # AJUSTA ESTO
CORPUS_PATH=./data/train
TEST_PATH=./data/test
EXP_BASE=./exp

echo "=== PASO 1: Alinea nuevos datos con modelo antiguo ==="
# Asume que ya tienes exp/tri1/final.mdl (tu modelo de 7 min)

# Extrae features de nuevos datos si no las tienes
cd $CORPUS_PATH
feat-to-dim scp:feats.scp ark,t:- | head -1
# Si esto falla, corre:
# mfcc.sh --use-energy false --energy-floor 0.0 \
#   data/train data/mfcc/train mfcc_cmvn_train

echo "Alineando con modelo antiguo..."
align-equal-compiled $EXP_BASE/tri1/final.mdl \
  scp:$CORPUS_PATH/feats.scp \
  ark:$CORPUS_PATH/text \
  ark:ali_new_data.ark 2>&1 | tee align.log

# Cuenta cuántos alinearon exitosamente
SUCCESS=$(grep -c "Aligning utterance" align.log)
echo "Utterances alineados exitosamente: $SUCCESS"

echo ""
echo "=== PASO 2: Re-entrena con TODOS los datos ==="
echo "Esto tardará ~2 horas. Mientras tanto, abre otra terminal y escribe la tesis."
echo ""

# Combina alineaciones (simplificado - en realidad necesitas concatenar ARK files)
# Para la versión simplificada, entrena directo con MLE

cd $EXP_BASE
mkdir -p tri1_iter2

# Entrena triphone con datos combinados (esto es la línea clave)
# Asume que tienes features de TODOS tus datos en $CORPUS_PATH/feats.scp
steps/train_deltas.sh --boost-silence 1.25 \
  2000 10000 \
  $CORPUS_PATH \
  data/lang \
  $EXP_BASE/mono \
  $EXP_BASE/tri1_iter2 2>&1 | tee tri1_iter2.log

echo "Entrenamiento completado. Resultados en $EXP_BASE/tri1_iter2/"

# Verifica que entrenó correctamente
if [ -f $EXP_BASE/tri1_iter2/final.mdl ]; then
    echo "✓ Modelo final exitoso"
else
    echo "✗ ERROR: Modelo no se creó"
    exit 1
fi

echo "=== FIN DEL ENTRENAMIENTO ==="
