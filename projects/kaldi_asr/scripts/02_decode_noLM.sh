#!/bin/bash
# Script 2: DECODIFICACION Y WER
# Úsalo así: bash decode_and_wer.sh

KALDI_ROOT=/path/to/kaldi  # AJUSTA
EXP_BASE=./exp
TEST_PATH=./data/test

echo "=== DECODIFICACION SIN MODELO DE LENGUAJE ==="

# 1. Decodifica
mkdir -p $EXP_BASE/tri1_iter2/decode_test_noLM

decode --acoustic-scale=0.1 --beam=15.0 --lattice-beam=8.0 \
  --max-active=7000 --frame-subsampling-factor=3 \
  $EXP_BASE/tri1_iter2/graph_noLM \
  "ark,s,cs:apply-cmvn --norm-vars=false --utt2spk=ark:$TEST_PATH/utt2spk scp:$TEST_PATH/cmvn.scp scp:$TEST_PATH/feats.scp ark:- |" \
  ark:$EXP_BASE/tri1_iter2/decode_test_noLM/lat.JOB.ark \
  2>&1 | tee $EXP_BASE/tri1_iter2/decode_test_noLM/decode.log

# 2. Convierte lattice a best path (palabras)
lattice-best-path --acoustic-scale=0.1 \
  "ark:gunzip -c $EXP_BASE/tri1_iter2/decode_test_noLM/lat.*.ark.gz|" \
  ark,t:$EXP_BASE/tri1_iter2/decode_test_noLM/one-best.tra 2>&1

# 3. Convierte integer a palabras (si es necesario)
# Si tus palabras ya están en texto, salta esto
# utils/int2sym.pl -f 2- data/lang/words.txt \
#   $EXP_BASE/tri1_iter2/decode_test_noLM/one-best.tra > \
#   $EXP_BASE/tri1_iter2/decode_test_noLM/one-best.txt

# 4. Calcula WER
echo ""
echo "=== CALCULANDO WER SIN LM ==="
compute-wer --text \
  ark:$TEST_PATH/text \
  ark:$EXP_BASE/tri1_iter2/decode_test_noLM/one-best.tra \
  2>&1 | tee $EXP_BASE/tri1_iter2/wer_noLM.txt

WER_NOLM=$(grep "Overall" $EXP_BASE/tri1_iter2/wer_noLM.txt | awk '{print $2}')
echo "✓ WER sin LM: $WER_NOLM"
echo ""

# Extrae solo el número WER para table
echo "$WER_NOLM" > /tmp/wer_nolm_value.txt
