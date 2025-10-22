import argparse
import pandas as pd
import logging
from utils import normalize_string, split_assignees, extract_first_date, extract_last_percentage

REQUIRED_COLUMNS = [
    'Assignee Details Name', 'Patent Number', 'Publication Date', 'Title',
    'Patent Valuation Score Technology', 'Patent Valuation Score Legal', 'Patent Valuation Score Citation'
]

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.StreamHandler()]
    )

def validate_columns(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        logging.error(f"Missing required columns: {missing}")
        raise ValueError(f"Missing required columns: {missing}")
    logging.info("All required columns are present.")

def dedupe_family(df):
    logging.info("Deduplicating families...")
    # Prefer Patent Number2 or family ID if exists, else use heuristic
    if 'Patent Number2' in df.columns:
        df['family_key'] = df['Patent Number2'].fillna('')
    else:
        df['family_key'] = df.apply(lambda row: normalize_string(row['Title']) + '|' + str(row['Publication Date']), axis=1)
    # Aggregate by family_key
    agg_funcs = {
        'Patent Number': 'first',
        'Patent Number2': 'first' if 'Patent Number2' in df.columns else (lambda x: ''),
        'Patent Valuation Score Technology': 'mean',
        'Patent Valuation Score Legal': 'mean',
        'Patent Valuation Score Citation': 'mean',
        'Country Code': lambda x: list(set(x)),
        'Assignee Details Name': lambda x: list(set(sum([split_assignees(a) for a in x], []))),
        'Publication Date': 'max',
        'Title': 'first',
    }
    # Only include keys that exist in df
    agg_funcs = {k: v for k, v in agg_funcs.items() if k in df.columns}
    df_agg = df.groupby('family_key').agg(agg_funcs).reset_index()
    df_agg['Family_Size'] = df.groupby('family_key').size().values
    logging.info(f"Deduplication complete. {len(df_agg)} families found.")
    return df_agg

def clean_and_parse(input_path, output_path, config=None):
    logging.info(f"Reading input file: {input_path}")
    df = pd.read_excel(input_path)
    validate_columns(df)
    logging.info("Cleaning columns...")
    # Clean columns
    df['Publication Date'] = df['Publication Date'].astype(str).apply(extract_first_date)
    for col in ['Patent Valuation Score Technology', 'Patent Valuation Score Legal', 'Patent Valuation Score Citation']:
        df[col] = df[col].astype(str).apply(extract_last_percentage)
    df['Assignee Details Name'] = df['Assignee Details Name'].astype(str).apply(lambda x: '\n'.join(split_assignees(x)))
    df = dedupe_family(df)
    logging.info(f"Saving cleaned data to: {output_path}")
    df.to_excel(output_path, index=False)
    logging.info("Parsing and cleaning completed successfully.")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Parse and clean patent Excel file.")
    parser.add_argument('--input', required=True, help='Input Excel file path')
    parser.add_argument('--output', required=False, help='Output cleaned Excel file path')
    parser.add_argument('--config', required=False, help='Config YAML path')
    args = parser.parse_args()
    config = None
    output_path = args.output
    if args.config:
        from utils import load_config
        config = load_config(args.config)
        if not output_path and config and 'paths' in config and 'cleaned_output' in config['paths']:
            output_path = config['paths']['cleaned_output']
    if not output_path:
        raise ValueError('Output path must be provided via CLI or config.yaml')
    clean_and_parse(args.input, output_path, config)

if __name__ == "__main__":
    main()
