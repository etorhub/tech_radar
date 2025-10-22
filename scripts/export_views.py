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


def export_internal(df, output_path):
    logging.info(f"Exportando vista interna a: {output_path}")
    df.to_excel(output_path, index=False)
    logging.info("Vista interna exportada.")

def export_public(df, output_path):
    logging.info(f"Exportando vista pública a: {output_path}")
    # Agrupación y anonimización
    group_cols = ['Primary_Mission', 'Primary_Domain']
    agg = {
        'family_key': 'count',
        'PCT_Flag': 'mean' if 'PCT_Flag' in df.columns else 'first',
        'TRL_Category': lambda x: x.value_counts().to_dict(),
        'Technology_Norm': 'mean' if 'Technology_Norm' in df.columns else 'first'
    }
    public_df = df.groupby(group_cols).agg(agg).reset_index()
    public_df = public_df.rename(columns={'family_key': 'families_count', 'Technology_Norm': 'avg_Technology'})
    # No incluir datos sensibles
    public_df.to_csv(output_path, index=False)
    logging.info("Vista pública exportada.")

def process(input_path, internal_path, public_path, config_path):
    logging.info(f"Leyendo archivo procesado: {input_path}")
    df = pd.read_excel(input_path)
    config = load_config(config_path)
    export_internal(df, internal_path)
    export_public(df, public_path)

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Export internal and public views from processed data.")
    parser.add_argument('--input', required=True, help='Input processed Excel file path')
    parser.add_argument('--public', required=False, help='Output public CSV file path')
    parser.add_argument('--config', required=True, help='Config YAML path')
    args = parser.parse_args()
    from utils import load_config
    config = load_config(args.config)
    public_path = args.public or config['paths'].get('public_output')
    internal_path = args.input.replace('.xlsx', '_internal.xlsx')
    if not public_path:
        raise ValueError('Public output path must be provided via CLI or config.yaml')
    process(args.input, internal_path, public_path, args.config)

if __name__ == "__main__":
    main()
