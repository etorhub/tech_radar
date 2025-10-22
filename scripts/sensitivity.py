import argparse
import pandas as pd
import logging
from utils import load_config
import numpy as np

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.StreamHandler()]
    )


def compute_fit_index(df, weights):
    max_tech = df['Patent Valuation Score Technology'].max()
    df['Technology_Norm'] = df['Patent Valuation Score Technology'] / max_tech * 100 if max_tech else 0
    df['TRL_Fit_Index_raw'] = (
        weights['technology'] * df['Technology_Norm'] +
        weights['legal'] * df['Patent Valuation Score Legal'] +
        weights['citation'] * df['Patent Valuation Score Citation'] +
        weights['freshness'] * df.get('Freshness_Flag', 1) * 100 +
        weights['pct'] * df.get('PCT_Flag', 1) * 100
    )
    max_fit = df['TRL_Fit_Index_raw'].max()
    df['TRL_Fit_Index'] = df['TRL_Fit_Index_raw'] / max_fit * 100 if max_fit else 0
    return df

def assign_categories(df, thresholds):
    df['TRL_Category'] = pd.cut(
        df['TRL_Fit_Index'],
        bins=[-float('inf'), thresholds['b_cut'], thresholds['a_cut'], float('inf')],
        labels=['C', 'B', 'A']
    )
    return df

def sensitivity_analysis(input_path, config_path, output_path):
    logging.info(f"Leyendo archivo procesado: {input_path}")
    df = pd.read_excel(input_path)
    config = load_config(config_path)
    weights = config['weights']
    thresholds = config['thresholds']
    results = []
    # Vary each weight +/- 20% in steps
    for key in weights:
        for delta in np.linspace(-0.2, 0.2, 5):
            new_weights = weights.copy()
            new_weights[key] = max(0, weights[key] * (1 + delta))
            # Normalize weights to sum to 1
            total = sum(new_weights.values())
            new_weights = {k: v / total for k, v in new_weights.items()}
            df_mod = compute_fit_index(df.copy(), new_weights)
            df_mod = assign_categories(df_mod, thresholds)
            counts = df_mod['TRL_Category'].value_counts().to_dict()
            results.append({
                'weight': key,
                'delta': delta,
                'A_count': counts.get('A', 0),
                'B_count': counts.get('B', 0),
                'C_count': counts.get('C', 0),
                'weights': new_weights
            })
    res_df = pd.DataFrame(results)
    logging.info(f"Guardando resultados de sensibilidad en: {output_path}")
    res_df.to_excel(output_path, index=False)
    logging.info("Análisis de sensibilidad completado.")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Sensitivity analysis of TRL2–4 Fit Index weights.")
    parser.add_argument('--input', required=True, help='Input processed Excel file path')
    parser.add_argument('--config', required=True, help='Config YAML path')
    parser.add_argument('--output', required=False, help='Output Excel file path for sensitivity results')
    args = parser.parse_args()
    from utils import load_config
    config = load_config(args.config)
    output_path = args.output or config['paths'].get('sensitivity_output')
    if not output_path:
        raise ValueError('Output path for sensitivity results must be provided via CLI or config.yaml')
    sensitivity_analysis(args.input, args.config, output_path)

if __name__ == "__main__":
    main()
