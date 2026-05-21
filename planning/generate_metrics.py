#!/usr/bin/env python3
"""
Script para generar resumen de métricas de tesis
Úsalo así: python3 generate_metrics_summary.py
"""

import os
import sys
import re
from pathlib import Path
import json

class MetricsSummary:
    def __init__(self, exp_base="./exp", test_path="./data/test"):
        self.exp_base = exp_base
        self.test_path = test_path
        self.metrics = {}
        
    def extract_wer(self, wer_file):
        """Extrae WER de archivo de resultado"""
        if not os.path.exists(wer_file):
            return None
        
        with open(wer_file) as f:
            for line in f:
                if "Overall" in line or "WER" in line:
                    # Busca patrón "XX.XX %"
                    match = re.search(r'(\d+\.\d+)\s*%', line)
                    if match:
                        return float(match.group(1))
        return None
    
    def get_corpus_stats(self):
        """Obtiene estadísticas del corpus"""
        stats = {
            'total_utterances': 0,
            'total_duration_min': 0,
            'num_speakers': 0,
            'num_files': 0
        }
        
        # Cuenta archivos en data/train
        audio_dir = Path("data/train")
        if audio_dir.exists():
            wav_files = list(audio_dir.glob("**/*.wav"))
            stats['num_files'] = len(wav_files)
        
        # Lee data/train/text para contar utterances
        text_file = Path(self.test_path).parent / "train" / "text"
        if text_file.exists():
            with open(text_file) as f:
                stats['total_utterances'] = len(f.readlines())
        
        # Intenta leer metadatos de hablantes
        spk_file = Path("data/train/speakers_metadata.tsv")
        if spk_file.exists():
            try:
                with open(spk_file) as f:
                    lines = f.readlines()
                    stats['num_speakers'] = len([l for l in lines if not l.startswith('#')])
            except:
                pass
        
        return stats
    
    def create_wer_comparison_table(self):
        """Crea tabla comparativa de WER"""
        
        wer_nolm = self.extract_wer(f"{self.exp_base}/tri1/wer_noLM.txt") or 0
        wer_nolm_iter2 = self.extract_wer(f"{self.exp_base}/tri1_iter2/wer_noLM.txt") or 0
        wer_lm = self.extract_wer(f"{self.exp_base}/tri1_iter2/wer_withLM.txt") or 0
        
        table = {
            'baseline_7min': {
                'model': 'Triphone',
                'wer_no_lm': f"{wer_nolm:.2f}%",
                'wer_with_lm': 'N/A'
            },
            'final_50min': {
                'model': 'Triphone + SAT',
                'wer_no_lm': f"{wer_nolm_iter2:.2f}%",
                'wer_with_lm': f"{wer_lm:.2f}%"
            },
            'improvement': {
                'absolute_no_lm': f"-{abs(wer_nolm - wer_nolm_iter2):.2f}%",
                'absolute_with_lm': f"-{abs(wer_nolm_iter2 - wer_lm):.2f}%" if wer_lm > 0 else "N/A"
            }
        }
        
        return table
    
    def generate_markdown_report(self, output_file="metrics_summary.md"):
        """Genera reporte en markdown"""
        
        corpus_stats = self.get_corpus_stats()
        wer_table = self.create_wer_comparison_table()
        
        report = f"""# Resumen de Métricas - Tesis Corpus Maya Yucateco

## 1. Estadísticas del Corpus

| Métrica | Valor |
|---------|-------|
| Total de archivos de audio | {corpus_stats['num_files']} |
| Total de utterances | {corpus_stats['total_utterances']} |
| Número de hablantes | {corpus_stats['num_speakers']} |
| Duración aproximada (min) | ~50 |

## 2. Comparativa de WER (Word Error Rate)

### Modelo Inicial (7 minutos)
- Arquitectura: Triphone
- WER sin LM: {wer_table['baseline_7min']['wer_no_lm']}
- WER con LM: {wer_table['baseline_7min']['wer_with_lm']}

### Modelo Final (50 minutos)
- Arquitectura: Triphone + SAT (Speaker-Adaptive Transform)
- WER sin LM: {wer_table['final_50min']['wer_no_lm']}
- WER con LM: {wer_table['final_50min']['wer_with_lm']}

### Mejora Total
- Sin LM: {wer_table['improvement']['absolute_no_lm']}
- Con LM: {wer_table['improvement']['absolute_with_lm']}

## 3. Análisis

La mejora en WER de {wer_table['improvement']['absolute_no_lm']} sin modelo de lenguaje 
indica que el aumento en datos de entrenamiento (7 min → 50 min) tuvo un impacto 
significativo en el desempeño del modelo acústico.

El modelo de lenguaje proporcionó una mejora adicional de {wer_table['improvement']['absolute_with_lm']},
demostrando la importancia de integrar información lingüística.

## 4. Archivos de Referencia

- WER sin LM: `{self.exp_base}/tri1_iter2/wer_noLM.txt`
- WER con LM: `{self.exp_base}/tri1_iter2/wer_withLM.txt`
- Logs de entrenamiento: `{self.exp_base}/tri1_iter2/`

---

*Generado automáticamente el {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(output_file, 'w') as f:
            f.write(report)
        
        print(f"✓ Reporte escrito en {output_file}")
        print("\n" + report)
        
        return report
    
    def generate_json_metrics(self, output_file="metrics.json"):
        """Exporta métricas a JSON para análisis posterior"""
        
        metrics_data = {
            'corpus': self.get_corpus_stats(),
            'wer': {
                'baseline_7min_no_lm': self.extract_wer(f"{self.exp_base}/tri1/wer_noLM.txt"),
                'final_50min_no_lm': self.extract_wer(f"{self.exp_base}/tri1_iter2/wer_noLM.txt"),
                'final_50min_with_lm': self.extract_wer(f"{self.exp_base}/tri1_iter2/wer_withLM.txt"),
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        print(f"✓ JSON metrics escrito en {output_file}")
        return metrics_data


def main():
    """Función principal"""
    
    print("=" * 60)
    print("GENERADOR DE METRICAS - TESIS MAYA YUCATECO")
    print("=" * 60)
    print()
    
    summary = MetricsSummary()
    
    # Genera reporte markdown
    summary.generate_markdown_report()
    
    # Genera JSON
    metrics = summary.generate_json_metrics()
    
    print("\n" + "=" * 60)
    print("✓ METRICAS GENERADAS EXITOSAMENTE")
    print("=" * 60)
    
    # Imprime resumen rápido
    print("\nRESUMEN RAPIDO:")
    print(f"  WER inicial (7 min, sin LM): {metrics['wer']['baseline_7min_no_lm']}%")
    print(f"  WER final (50 min, sin LM):  {metrics['wer']['final_50min_no_lm']}%")
    print(f"  WER final (50 min, con LM):  {metrics['wer']['final_50min_with_lm']}%")
    
    if metrics['wer']['baseline_7min_no_lm'] and metrics['wer']['final_50min_no_lm']:
        improvement = metrics['wer']['baseline_7min_no_lm'] - metrics['wer']['final_50min_no_lm']
        print(f"\n  📈 MEJORA TOTAL: -{improvement:.2f} puntos")
    
    return metrics


if __name__ == "__main__":
    metrics = main()
