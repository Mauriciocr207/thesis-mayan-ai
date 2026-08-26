#!/bin/bash
# Script 4: DECODIFICACION CON LM + GENERACION DE METRICAS
# Úsalo así: bash decode_with_lm.sh

KALDI_ROOT=/path/to/kaldi
EXP_BASE=./exp
TEST_PATH=./data/test
LM_DIR=./exp/lm

echo "=== DECODIFICACION CON MODELO DE LENGUAJE ==="

mkdir -p $EXP_BASE/tri1_iter2/decode_test_withLM

# 1. Decodifica con LM rescoring
# (nota: esto es simplificado, la forma real depende de tu setup)

lattice-rescore --acoustic-scale=0.1 \
  "ark:gunzip -c $EXP_BASE/tri1_iter2/decode_test_noLM/lat.*.ark.gz|" \
  "fstproject --project_output $LM_DIR/lm.fst |" \
  ark:$EXP_BASE/tri1_iter2/decode_test_withLM/lat.ark 2>&1

# 2. Best path
lattice-best-path --acoustic-scale=0.1 \
  "ark:gunzip -c $EXP_BASE/tri1_iter2/decode_test_withLM/lat.*.ark.gz|" \
  ark,t:$EXP_BASE/tri1_iter2/decode_test_withLM/one-best.tra 2>&1

# 3. Calcula WER
echo ""
echo "=== CALCULANDO WER CON LM ==="
compute-wer --text \
  ark:$TEST_PATH/text \
  ark:$EXP_BASE/tri1_iter2/decode_test_withLM/one-best.tra \
  2>&1 | tee $EXP_BASE/tri1_iter2/wer_withLM.txt

WER_LM=$(grep "Overall" $EXP_BASE/tri1_iter2/wer_withLM.txt | awk '{print $2}')
echo "✓ WER con LM: $WER_LM"

# Guarda valor
echo "$WER_LM" > /tmp/wer_lm_value.txt
