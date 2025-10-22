import argparse
import pandas as pd
import logging
import json
from utils import load_config

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.StreamHandler()]
    )



def load_cpc_map(cpc_map_path):
    df = pd.read_csv(cpc_map_path)
    df['prefix'] = df['prefix'].astype(str)
    return df

def match_cpc_codes(codes, cpc_map):
    matches = []
    for code in codes:
        code = code.strip().upper()
        matched = cpc_map[cpc_map['prefix'].apply(lambda p: code.startswith(p.upper()))]
        if not matched.empty:
            # Pick highest confidence, then longest prefix
            best = matched.sort_values(['confidence', 'prefix'], ascending=[False, False]).iloc[0]
            matches.append(best)
    return matches

def map_row(row, cpc_map):
    codes = str(row.get('CPC/IPC Codes', '')).replace(';', ',').split(',')
    matches = match_cpc_codes(codes, cpc_map)
    if matches:
        # Primary: highest confidence, then longest prefix
        primary = sorted(matches, key=lambda m: (m['confidence'], len(m['prefix'])), reverse=True)[0]
        primary_domain = primary['tech_domain']
        primary_mission = primary['mission_code']
        domain_weights = {}
        total = len(matches)
        for m in matches:
            domain_weights[m['tech_domain']] = domain_weights.get(m['tech_domain'], 0) + 1/total
        matched_prefixes = [m['prefix'] for m in matches]
        mapping_method = 'CPC'
    else:
        primary_domain = ''
        primary_mission = 'M0'
        domain_weights = {}
        matched_prefixes = []
        mapping_method = 'UNMAPPED'
    return pd.Series({
        'Primary_Domain': primary_domain,
        'Primary_Mission': primary_mission,
        'Domain_Weights_JSON': json.dumps(domain_weights),
        'Matched_Prefixes': ';'.join(matched_prefixes),
        'Mapping_Method': mapping_method
    })

def process(input_path, output_path, cpc_map_path, config_path):
    logging.info(f"Reading input file: {input_path}")
    df = pd.read_excel(input_path)
    config = load_config(config_path)
    cpc_map = load_cpc_map(cpc_map_path)
    logging.info("Mapping CPC/IPC codes to domains and missions...")
    mapped = df.apply(lambda row: map_row(row, cpc_map), axis=1)
    df = pd.concat([df, mapped], axis=1)
    logging.info(f"Saving output to: {output_path}")
    df.to_excel(output_path, index=False)
    logging.info("Mapping completed.")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Map CPC/IPC codes to tech domains and mission codes.")
    parser.add_argument('--input', required=True, help='Input Excel file path')
    parser.add_argument('--output', required=False, help='Output Excel file path')
    parser.add_argument('--cpc-map', required=False, help='CPC/IPC map CSV path')
    parser.add_argument('--config', required=True, help='Config YAML path')
    args = parser.parse_args()
    from utils import load_config
    config = load_config(args.config)
    output_path = args.output or config['paths'].get('missions_output')
    cpc_map_path = args.cpc_map or config['paths'].get('cpc_map')
    if not output_path or not cpc_map_path:
        raise ValueError('Output and cpc_map paths must be provided via CLI or config.yaml')
    process(args.input, output_path, cpc_map_path, args.config)

if __name__ == "__main__":
    main()
