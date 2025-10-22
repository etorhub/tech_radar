import argparse
import pandas as pd
import logging
from utils import load_config
import re

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.StreamHandler()]
    )


def load_list(path):
    try:
        return set(pd.read_csv(path, header=None)[0].astype(str).str.upper())
    except Exception:
        return set()

def is_company(name, whitelist):
    # Regex for legal forms
    company_regex = r"\\b(SL|SA|SLU|SLL|GMBH|LTD|LLC|INC|CORP|SAS|BV|AG|PLC|SPA)\\b"
    name_norm = name.upper()
    if name_norm in whitelist:
        return False
    return bool(re.search(company_regex, name_norm))

def apply_flags(df, whitelist, blacklist, config):
    logging.info("Applying Venture Builder flags...")
    # Industry_CoOwner_Flag
    df['Industry_CoOwner_Flag'] = df['Assignee Details Name'].apply(
        lambda names: int(any(is_company(n, whitelist) for n in str(names).split('\n')))
    )
    # Alive_Flag
    if 'Dead or Alive' in df.columns:
        df['Alive_Flag'] = df['Dead or Alive'].astype(str).str.upper().map({'ALIVE': 1, 'DEAD': 0}).fillna(0).astype(int)
    # Litigation_Flag
    if 'Litigation Exists' in df.columns:
        df['Litigation_Flag'] = df['Litigation Exists'].astype(str).str.upper().map({'YES': 1, 'NO': 0}).fillna(0).astype(int)
    # VB_Eligible
    df['VB_Eligible'] = (
        (df['Industry_CoOwner_Flag'] == 0) &
        (df.get('Freshness_Flag', 1) == 1) &
        ((df.get('Alive_Flag', 1) == 1) if config['eligibility'].get('require_alive', False) else True) &
        ((df.get('Litigation_Flag', 0) == 0) if config['eligibility'].get('exclude_litigation', False) else True)
    ).astype(int)
    # VB_Exclusion_Reason
    def exclusion_reason(row):
        if row['Industry_CoOwner_Flag'] == 1:
            return 'company_coprop'
        if row.get('Freshness_Flag', 1) == 0:
            return 'stale_ip'
        if row.get('Alive_Flag', 1) == 0:
            return 'dead'
        if row.get('Litigation_Flag', 0) == 1:
            return 'litigation'
        return 'other'
    df['VB_Exclusion_Reason'] = df.apply(lambda row: exclusion_reason(row) if row['VB_Eligible'] == 0 else '', axis=1)
    logging.info("Flags applied.")
    return df

def process(input_path, output_path, whitelist_path, blacklist_path, config_path):
    logging.info(f"Reading input file: {input_path}")
    df = pd.read_excel(input_path)
    config = load_config(config_path)
    whitelist = load_list(whitelist_path)
    blacklist = load_list(blacklist_path)
    df = apply_flags(df, whitelist, blacklist, config)
    logging.info(f"Saving output to: {output_path}")
    df.to_excel(output_path, index=False)
    logging.info("Venture Builder flagging completed.")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Apply Venture Builder flags and exclusion rules.")
    parser.add_argument('--input', required=True, help='Input Excel file path')
    parser.add_argument('--output', required=False, help='Output Excel file path')
    parser.add_argument('--whitelist', required=False, help='Whitelist CSV path')
    parser.add_argument('--blacklist', required=False, help='Blacklist CSV path')
    parser.add_argument('--config', required=True, help='Config YAML path')
    args = parser.parse_args()
    from utils import load_config
    config = load_config(args.config)
    output_path = args.output or config['paths'].get('flags_output')
    whitelist_path = args.whitelist or config['paths'].get('whitelist')
    blacklist_path = args.blacklist or config['paths'].get('blacklist')
    if not output_path or not whitelist_path or not blacklist_path:
        raise ValueError('Output, whitelist, and blacklist paths must be provided via CLI or config.yaml')
    process(args.input, output_path, whitelist_path, blacklist_path, args.config)

if __name__ == "__main__":
    main()
