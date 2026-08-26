#!/bin/bash
# Script 3: MODELO DE LENGUAJE SIMPLE
# Úsalo así: bash build_lm.sh

KALDI_ROOT=/path/to/kaldi
CORPUS_PATH=./data/train
LM_DIR=./exp/lm

mkdir -p $LM_DIR

echo "=== CONSTRUYENDO MODELO DE LENGUAJE TRIGRAMA ==="

# Extrae palabras del corpus
echo "Extrayendo vocabulario..."
cat $CORPUS_PATH/text | awk '{$1=""; print}' | tr ' ' '\n' | sort | uniq > $LM_DIR/words.txt

echo "Palabras únicas: $(wc -l < $LM_DIR/words.txt)"

# OPCION A: Si tienes SRILM instalado (mucho más rápido)
if command -v ngram-count &> /dev/null; then
    echo "Usando SRILM..."
    
    # Crea archivo de texto simple
    cat $CORPUS_PATH/text | awk '{$1=""; print}' > $LM_DIR/train.txt
    
    # Entrena trigrama
    ngram-count -text $LM_DIR/train.txt \
        -lm $LM_DIR/lm.arpa \
        -interpolate -kndiscount -order 3 \
        -vocab $LM_DIR/words.txt 2>&1 | tee $LM_DIR/lm_train.log
    
    echo "✓ ARPA model en: $LM_DIR/lm.arpa"
    
# OPCION B: Si no tienes SRILM (usa script Python simple)
else
    echo "SRILM no encontrado. Usando método alternativo..."
    
    # Python script para trigrama simple
    python3 << 'EOF'
import sys
from collections import defaultdict, Counter

# Lee datos
with open('./data/train/text') as f:
    text = ' '.join(line.split()[1:] for line in f)

words = text.split()
vocab = set(words)

# Cuenta unigramas, bigramas, trigramas
unigram = Counter(words)
bigram = Counter()
trigram = Counter()

for i in range(len(words) - 2):
    bigram[(words[i], words[i+1])] += 1
    trigram[(words[i], words[i+1], words[i+2])] += 1

# Escribe ARPA (formato simplificado)
with open('./exp/lm/lm_simple.arpa', 'w') as f:
    f.write("\\data\\\n")
    f.write(f"ngram 1={len(unigram)}\n")
    f.write(f"ngram 2={len(bigram)}\n")
    f.write(f"ngram 3={len(trigram)}\n")
    f.write("\\\\\n")
    
    # Unigramas
    f.write("\\1-grams:\n")
    total = sum(unigram.values())
    for word, count in sorted(unigram.items(), key=lambda x: -x[1])[:1000]:
        prob = count / total
        f.write(f"{prob:.6f} {word}\n")
    f.write("\n")
    
    # Bigramas
    f.write("\\2-grams:\n")
    for (w1, w2), count in sorted(bigram.items(), key=lambda x: -x[1])[:5000]:
        if w1 in vocab and w2 in vocab:
            prob = count / unigram[w1]
            f.write(f"{prob:.6f} {w1} {w2}\n")
    f.write("\n")
    
    # Trigramas
    f.write("\\3-grams:\n")
    for (w1, w2, w3), count in sorted(trigram.items(), key=lambda x: -x[1])[:5000]:
        if (w1, w2) in bigram:
            prob = count / bigram[(w1, w2)]
            f.write(f"{prob:.6f} {w1} {w2} {w3}\n")
    f.write("\\end\\\n")

print("✓ LM simple creado")
EOF
fi

echo ""
echo "=== CONVIRTIENDO ARPA A FST ==="
# Convierte a FST (formato Kaldi)

if [ -f $LM_DIR/lm.arpa ]; then
    arpa2fst $LM_DIR/lm.arpa $LM_DIR/lm.fst 2>&1
    echo "✓ FST modelo de lenguaje listo"
else
    echo "⚠ No se encontró lm.arpa, revisa el proceso anterior"
fi

echo ""
echo "=== MODELO DE LENGUAJE COMPLETADO ==="
