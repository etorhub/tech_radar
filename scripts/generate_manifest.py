import argparse
import pandas as pd
import yaml
import json
import logging
import hashlib
import os
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.StreamHandler()]
    )

def file_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def manifest(input_path, config_path, output_path, period, pipeline_version):
    logging.info(f"Generando manifiesto de ejecución en: {output_path}")
    df = pd.read_excel(input_path)
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    # Only include config variables that were actually used
    used_config = {}
    # weights and thresholds always used
    if 'weights' in config:
        used_config['weights'] = config['weights']
    if 'thresholds' in config:
        used_config['thresholds'] = config['thresholds']
    # eligibility used if VB_Eligible present
    if 'VB_Eligible' in df.columns and 'eligibility' in config:
        used_config['eligibility'] = config['eligibility']
    # paths: only those used in this run
    if 'paths' in config:
        used_paths = {}
        for k, v in config['paths'].items():
            if k in ['whitelist', 'blacklist', 'cpc_map', 'dashboard_path', 'dasboard_path', 'figures_dir', 'public_output', 'cleaned_output', 'fit_index_output', 'flags_output', 'missions_output', 'sensitivity_output', 'previous_snapshot', 'delta_out']:
                used_paths[k] = v
        if used_paths:
            used_config['paths'] = used_paths
    # missions: only if used in mapping
    if 'Primary_Mission' in df.columns and 'missions' in config:
        used_config['missions'] = config['missions']
    manifest = {
        'timestamp': datetime.now().isoformat(),
        'input_file': input_path,
        'input_hash': file_hash(input_path),
        'pipeline_version': pipeline_version,
        'config': used_config,
        'period': period,
        'counts': {
            'total': len(df),
            'A': int((df['TRL_Category'] == 'A').sum()) if 'TRL_Category' in df.columns else None,
            'B': int((df['TRL_Category'] == 'B').sum()) if 'TRL_Category' in df.columns else None,
            'C': int((df['TRL_Category'] == 'C').sum()) if 'TRL_Category' in df.columns else None,
            'VB_eligible': int(df.get('VB_Eligible', pd.Series([0]*len(df))).sum()),
        },
        'mapping': {
            'mapped_pct': 1 - (df['Primary_Mission'].eq('M0').mean() if 'Primary_Mission' in df.columns else 1),
            'unmapped_pct': df['Primary_Mission'].eq('M0').mean() if 'Primary_Mission' in df.columns else 1,
        },
        'timing': {
            'start': None,
            'end': None,
            'duration_sec': None
        }
    }
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    logging.info("Manifiesto guardado.")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Generate pipeline run manifest.")
    parser.add_argument('--input', required=True, help='Input processed Excel file path')
    parser.add_argument('--config', required=True, help='Config YAML path')
    parser.add_argument('--output', required=True, help='Output manifest JSON file path')
    parser.add_argument('--period', required=True, help='Period (YYYY_MM)')
    parser.add_argument('--version', required=True, help='Pipeline version string')
    args = parser.parse_args()
    manifest(args.input, args.config, args.output, args.period, args.version)

if __name__ == "__main__":
    main()
