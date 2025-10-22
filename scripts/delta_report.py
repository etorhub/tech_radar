import argparse
import pandas as pd
import logging
import os

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.StreamHandler()]
    )

def load_data(path):
    if not os.path.exists(path):
        logging.warning(f"Archivo previo no encontrado: {path}. Se asumirá que no hay datos previos.")
        return pd.DataFrame()
    return pd.read_excel(path)

def get_family_key(df):
    return df['family_key'] if 'family_key' in df.columns else df.index

def delta_report(current_path, previous_path, out_path):
    logging.info(f"Leyendo archivo actual: {current_path}")
    current = load_data(current_path)
    logging.info(f"Leyendo snapshot previo: {previous_path}")
    previous = load_data(previous_path)
    # NEW: familias en actual que no estaban en previo
    new_families = set(get_family_key(current)) - set(get_family_key(previous))
    df_new = current[current['family_key'].isin(new_families)]
    # DROPPED: familias en previo que no están en actual
    dropped_families = set(get_family_key(previous)) - set(get_family_key(current))
    df_dropped = previous[previous['family_key'].isin(dropped_families)] if not previous.empty else pd.DataFrame()
    # UPGRADED: B->A o C->A
    if not previous.empty:
        upgraded = current.merge(previous[['family_key', 'TRL_Category']], on='family_key', suffixes=('', '_prev'))
        df_upgraded = upgraded[((upgraded['TRL_Category_prev'] != 'A') & (upgraded['TRL_Category'] == 'A'))]
        # DOWNGRADED: A->B/C o B->C
        df_downgraded = upgraded[((upgraded['TRL_Category_prev'] == 'A') & (upgraded['TRL_Category'] != 'A')) |
                                 ((upgraded['TRL_Category_prev'] == 'B') & (upgraded['TRL_Category'] == 'C'))]
        # EXCLUDED_BY_RULE: VB_Eligible pasó de 1 a 0
        excluded = current.merge(previous[['family_key', 'VB_Eligible']], on='family_key', suffixes=('', '_prev'))
        df_excluded = excluded[(excluded['VB_Eligible_prev'] == 1) & (excluded['VB_Eligible'] == 0)]
    else:
        df_upgraded = pd.DataFrame()
        df_downgraded = pd.DataFrame()
        df_excluded = pd.DataFrame()
    # Guardar en Excel con pestañas
    logging.info(f"Guardando reporte mensual en: {out_path}")
    with pd.ExcelWriter(out_path) as writer:
        df_new.to_excel(writer, sheet_name='NEW', index=False)
        df_dropped.to_excel(writer, sheet_name='DROPPED', index=False)
        df_upgraded.to_excel(writer, sheet_name='UPGRADED', index=False)
        df_downgraded.to_excel(writer, sheet_name='DOWNGRADED', index=False)
        df_excluded.to_excel(writer, sheet_name='EXCLUDED_BY_RULE', index=False)
    logging.info("Reporte mensual generado.")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Generate Monthly Update delta report.")
    parser.add_argument('--current', required=True, help='Current processed Excel file path')
    parser.add_argument('--previous-snapshot', required=False, help='Previous snapshot Excel file path')
    parser.add_argument('--delta-out', required=False, help='Output Excel file path for delta report')
    parser.add_argument('--config', required=False, help='Config YAML path')
    args = parser.parse_args()
    previous_snapshot = args.previous_snapshot
    delta_out = args.delta_out
    if args.config:
        from utils import load_config
        config = load_config(args.config)
        if not previous_snapshot and config and 'paths' in config and 'previous_snapshot' in config['paths']:
            previous_snapshot = config['paths']['previous_snapshot']
        if not delta_out and config and 'paths' in config and 'delta_out' in config['paths']:
            delta_out = config['paths']['delta_out']
    if not previous_snapshot or not delta_out:
        raise ValueError('Previous snapshot and delta output paths must be provided via CLI or config.yaml')
    delta_report(args.current, previous_snapshot, delta_out)

if __name__ == "__main__":
    main()
