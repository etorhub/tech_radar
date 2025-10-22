import argparse
import pandas as pd
import logging
from utils import load_config

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.StreamHandler()]
    )


def compute_technology_norm(df):
    max_tech = df['Patent Valuation Score Technology'].max()
    df['Technology_Norm'] = df['Patent Valuation Score Technology'] / max_tech * 100 if max_tech else 0
    return df

def compute_flags(df, freshness_months):
    # Freshness Flag: 1 if PublicationDate <= freshness_months
    df['Publication Date'] = pd.to_datetime(df['Publication Date'], errors='coerce')
    latest_date = pd.Timestamp.now()
    df['Freshness_Flag'] = ((latest_date - df['Publication Date']).dt.days <= freshness_months * 30).astype(int)
    # PCT Flag: 1 if Patent Number contains WO
    df['PCT_Flag'] = df['Patent Number'].astype(str).str.contains('WO').astype(int)
    return df

def compute_fit_index(df, weights):
    df = compute_technology_norm(df)
    df = compute_flags(df, weights.get('freshness_months', 36))
    df['TRL_Fit_Index_raw'] = (
        weights['technology'] * df['Technology_Norm'] +
        weights['legal'] * df['Patent Valuation Score Legal'] +
        weights['citation'] * df['Patent Valuation Score Citation'] +
        weights['freshness'] * df['Freshness_Flag'] * 100 +
        weights['pct'] * df['PCT_Flag'] * 100
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

def process(input_path, output_path, config_path):
    logging.info(f"Reading input file: {input_path}")
    df = pd.read_excel(input_path)
    config = load_config(config_path)
    weights = config['weights']
    thresholds = config['thresholds']
    df = compute_fit_index(df, weights)
    df = assign_categories(df, thresholds)
    logging.info(f"Saving output to: {output_path}")
    df.to_excel(output_path, index=False)
    logging.info("TRL2–4 Fit Index calculation completed.")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Compute TRL2–4 Fit Index and assign categories.")
    parser.add_argument('--input', required=True, help='Input cleaned Excel file path')
    parser.add_argument('--output', required=False, help='Output Excel file path')
    parser.add_argument('--config', required=True, help='Config YAML path')
    args = parser.parse_args()
    from utils import load_config
    config = load_config(args.config)
    output_path = args.output
    if not output_path and config and 'paths' in config and 'fit_index_output' in config['paths']:
        output_path = config['paths']['fit_index_output']
    if not output_path:
        raise ValueError('Output path must be provided via CLI or config.yaml')
    process(args.input, output_path, args.config)

if __name__ == "__main__":
    main()
