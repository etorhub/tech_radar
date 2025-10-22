import argparse
import pandas as pd
import logging
import matplotlib.pyplot as plt
import os
from utils import load_config

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[logging.StreamHandler()]
    )

def radar_chart(df, outdir):
    logging.info("Generando Radar_TRL_Fit_ABC.png...")
    categories = ['A', 'B', 'C']
    metrics = ['Patent Valuation Score Technology', 'Patent Valuation Score Legal', 'Patent Valuation Score Citation']
    num_vars = len(metrics)
    angles = [n / float(num_vars) * 2 * 3.141592653589793 for n in range(num_vars)]
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    for cat in categories:
        # Get means for each metric, handle missing data
        values = [df[df['TRL_Category'] == cat][m].mean() if not df[df['TRL_Category'] == cat][m].isnull().all() else 0 for m in metrics]
        values += values[:1]  # close the polygon
        ax.plot(angles, values, label=cat)
        ax.fill(angles, values, alpha=0.1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_ylim(0, 100)
    ax.grid(True)
    plt.title('Radar TRL-Fit ABC')
    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'Radar_TRL_Fit_ABC.png'))
    plt.close()
    logging.info("Radar chart guardado.")

def top10_chart(df, outdir):
    logging.info("Generando Top10_TRL_Fit_Index.png...")
    top10 = df.nlargest(10, 'TRL_Fit_Index')
    plt.figure(figsize=(10, 6))
    plt.barh(top10['family_key'], top10['TRL_Fit_Index'])
    plt.xlabel('TRL Fit Index')
    plt.title('Top 10 TRL Fit Index')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'Top10_TRL_Fit_Index.png'))
    plt.close()
    logging.info("Top10 chart guardado.")

def trend_chart(df, outdir):
    logging.info("Generando Trend_Patents.png...")
    df['Publication Date'] = pd.to_datetime(df['Publication Date'], errors='coerce')
    trend = df.groupby(df['Publication Date'].dt.to_period('M')).size()
    trend.index = trend.index.astype(str)
    plt.figure(figsize=(10, 6))
    plt.plot(trend.index, trend.values, marker='o')
    plt.xlabel('Mes de publicación')
    plt.ylabel('Número de familias')
    plt.title('Trend Patents')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'Trend_Patents.png'))
    plt.close()
    logging.info("Trend chart guardado.")

def process(input_path, period, outdir, config_path):
    logging.info(f"Leyendo archivo procesado: {input_path}")
    df = pd.read_excel(input_path)
    os.makedirs(outdir, exist_ok=True)
    radar_chart(df, outdir)
    top10_chart(df, outdir)
    trend_chart(df, outdir)

    # Create Excel dashboard
    try:
        import xlsxwriter
    except ImportError:
        logging.error("xlsxwriter not installed. Run 'pip install xlsxwriter'.")
        return
    
    config = load_config(config_path)
    dashboard_root = config['paths'].get('dashboard_path') or config['paths'].get('dasboard_path') or 'dashboard/'
    dashboard_path = os.path.join(dashboard_root, f'Radar_Tecnologico_{period}.xlsx')
    workbook = xlsxwriter.Workbook(dashboard_path)

    # Overview sheet
    overview = workbook.add_worksheet('Overview')
    overview.write(0, 0, 'Radar Tecnológico Dashboard')
    overview.write(1, 0, 'Period:')
    overview.write(1, 1, period)
    overview.write(2, 0, 'Instructions:')
    overview.write(3, 0, 'This dashboard is auto-generated. See other sheets for charts and data.')

    # Radar chart sheet
    radar_sheet = workbook.add_worksheet('Radar_TRL_Fit')
    radar_img = os.path.join(outdir, 'Radar_TRL_Fit_ABC.png')
    radar_sheet.insert_image('B2', radar_img)

    # Top10 chart sheet
    top10_sheet = workbook.add_worksheet('Top10_TRL_Fit_Index')
    top10_img = os.path.join(outdir, 'Top10_TRL_Fit_Index.png')
    top10_sheet.insert_image('B2', top10_img)

    # Trend chart sheet
    trend_sheet = workbook.add_worksheet('Trend_Patents')
    trend_img = os.path.join(outdir, 'Trend_Patents.png')
    trend_sheet.insert_image('B2', trend_img)

    # Data sheet (public view)
    public_csv = os.path.join(os.path.dirname(input_path), f'TRL2-4_Fit_Index_{period}_public.csv')
    if os.path.exists(public_csv):
        public_df = pd.read_csv(public_csv)
        data_sheet = workbook.add_worksheet('Public_View')
        for col_idx, col in enumerate(public_df.columns):
            data_sheet.write(0, col_idx, col)
        for row_idx, row in enumerate(public_df.values):
            for col_idx, val in enumerate(row):
                data_sheet.write(row_idx + 1, col_idx, val)

    # Spin-off Candidates (A)
    spin_off_sheet = workbook.add_worksheet('Spin-off_Candidates_A')
    spin_off = df[(df['TRL_Category'] == 'A') & (df.get('VB_Eligible', 1) == 1)]
    if not spin_off.empty:
        for col_idx, col in enumerate(spin_off.columns):
            spin_off_sheet.write(0, col_idx, col)
        for row_idx, row in enumerate(spin_off.values):
            for col_idx, val in enumerate(row):
                # Fix: convert NaN/Inf to empty string for Excel
                if pd.isna(val) or (isinstance(val, float) and (pd.isnull(val) or pd.isna(val) or val == float('inf') or val == float('-inf'))):
                    spin_off_sheet.write(row_idx + 1, col_idx, '')
                else:
                    spin_off_sheet.write(row_idx + 1, col_idx, val)
    else:
        spin_off_sheet.write(0, 0, 'No spin-off candidates found.')

    # Heatmap Mission x Month
    heatmap_sheet = workbook.add_worksheet('Heatmap_Mission_Month')
    if 'Primary_Mission' in df.columns and 'Publication Date' in df.columns:
        df['Pub_Month'] = pd.to_datetime(df['Publication Date'], errors='coerce').dt.to_period('M').astype(str)
        heatmap = df.groupby(['Primary_Mission', 'Pub_Month']).size().unstack(fill_value=0)
        heatmap_sheet.write(0, 0, 'Primary_Mission')
        for col_idx, col in enumerate(heatmap.columns):
            heatmap_sheet.write(0, col_idx + 1, col)
        for row_idx, (mission, row) in enumerate(heatmap.iterrows()):
            heatmap_sheet.write(row_idx + 1, 0, mission)
            for col_idx, val in enumerate(row):
                heatmap_sheet.write(row_idx + 1, col_idx + 1, val)
    else:
        heatmap_sheet.write(0, 0, 'Insufficient data for heatmap.')

    # Pareto Titular
    pareto_sheet = workbook.add_worksheet('Pareto_Titular')
    if 'Assignee Details Name' in df.columns:
        pareto = df['Assignee Details Name'].value_counts().head(20)
        pareto_sheet.write(0, 0, 'Assignee')
        pareto_sheet.write(0, 1, 'Families_Count')
        for idx, (assignee, count) in enumerate(pareto.items()):
            pareto_sheet.write(idx + 1, 0, assignee)
            pareto_sheet.write(idx + 1, 1, count)
    else:
        pareto_sheet.write(0, 0, 'Assignee column not found.')

    # Cohorts
    cohorts_sheet = workbook.add_worksheet('Cohorts')
    if 'Publication Date' in df.columns:
        df['Pub_Year'] = pd.to_datetime(df['Publication Date'], errors='coerce').dt.year
        cohorts = df.groupby('Pub_Year').size()
        cohorts_sheet.write(0, 0, 'Year')
        cohorts_sheet.write(0, 1, 'Families_Count')
        for idx, (year, count) in enumerate(cohorts.items()):
            cohorts_sheet.write(idx + 1, 0, year)
            cohorts_sheet.write(idx + 1, 1, count)
    else:
        cohorts_sheet.write(0, 0, 'Publication Date column not found.')

    # Delta (Monthly Update)
    delta_sheet = workbook.add_worksheet('Delta')
    monthly_update_path = os.path.join(os.path.dirname(input_path), f'monthly_update_{period}.xlsx')
    try:
        monthly_update = pd.read_excel(monthly_update_path, sheet_name=None)
        for sheet_idx, (tab, tab_df) in enumerate(monthly_update.items()):
            delta_sheet.write(0, sheet_idx * 10, tab)
            for col_idx, col in enumerate(tab_df.columns):
                delta_sheet.write(1, sheet_idx * 10 + col_idx, col)
            for row_idx, row in enumerate(tab_df.values):
                for col_idx, val in enumerate(row):
                    delta_sheet.write(row_idx + 2, sheet_idx * 10 + col_idx, val)
    except Exception:
        delta_sheet.write(0, 0, 'Monthly update file not found or unreadable.')

    # Coverage KPI
    kpi_sheet = workbook.add_worksheet('Coverage_KPI')
    manifest_path = os.path.join(os.path.dirname(input_path), f'../logs/run_manifest_{period}.json')
    try:
        import json
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        kpi_sheet.write(0, 0, 'KPI')
        kpi_sheet.write(0, 1, 'Value')
        kpi_sheet.write(1, 0, '%M0 (Unmapped)')
        kpi_sheet.write(1, 1, manifest['mapping']['unmapped_pct'])
        kpi_sheet.write(2, 0, 'Total Families')
        kpi_sheet.write(2, 1, manifest['counts']['total'])
        # Top-5 unmapped CPC (placeholder)
        kpi_sheet.write(3, 0, 'Top-5 Unmapped CPC')
        kpi_sheet.write(3, 1, 'See mapping QA report')
    except Exception:
        kpi_sheet.write(0, 0, 'Manifest file not found or unreadable.')

    workbook.close()
    logging.info(f"Excel dashboard generado en: {dashboard_path}")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Generate charts from processed data.")
    parser.add_argument('--input', required=True, help='Input processed Excel file path')
    parser.add_argument('--period', required=True, help='Period (YYYY_MM)')
    parser.add_argument('--outdir', required=False, help='Output directory for figures')
    parser.add_argument('--config', required=True, help='Config YAML path')
    args = parser.parse_args()
    from utils import load_config
    config = load_config(args.config)
    outdir = args.outdir or config['paths'].get('figures_dir')
    if not outdir:
        raise ValueError('Output directory for figures must be provided via CLI or config.yaml')
    process(args.input, args.period, outdir, args.config)

if __name__ == "__main__":
    main()
