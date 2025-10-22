import subprocess
import sys
import os

# Placeholder for run_all.py
# Orchestrates the monthly pipeline execution.

def run_parse_patents(input_path, output_path, config_path=None):
    cmd = [sys.executable, 'scripts/parse_patents.py', '--input', input_path, '--output', output_path]
    if config_path:
        cmd += ['--config', config_path]
    subprocess.run(cmd, check=True)

def run_compute_fit_index(input_path, output_path, config_path):
    cmd = [sys.executable, 'scripts/compute_fit_index.py', '--input', input_path, '--output', output_path, '--config', config_path]
    subprocess.run(cmd, check=True)

def run_augment_flags(input_path, output_path, whitelist_path, blacklist_path, config_path):
    cmd = [sys.executable, 'scripts/augment_flags.py', '--input', input_path, '--output', output_path,
           '--whitelist', whitelist_path, '--blacklist', blacklist_path, '--config', config_path]
    subprocess.run(cmd, check=True)

def run_map_to_missions(input_path, output_path, cpc_map_path, config_path):
    cmd = [sys.executable, 'scripts/map_to_missions.py', '--input', input_path, '--output', output_path,
           '--cpc-map', cpc_map_path, '--config', config_path]
    subprocess.run(cmd, check=True)

def run_export_views(input_path, public_path, config_path):
    cmd = [sys.executable, 'scripts/export_views.py', '--input', input_path, '--public', public_path, '--config', config_path]
    subprocess.run(cmd, check=True)

def run_generate_charts(input_path, period, outdir, config_path):
    cmd = [sys.executable, 'scripts/generate_charts.py', '--input', input_path, '--period', period, '--outdir', outdir, '--config', config_path]
    subprocess.run(cmd, check=True)

def run_delta_report(current_path, previous_snapshot_path, delta_out_path):
    cmd = [sys.executable, 'scripts/delta_report.py', '--current', current_path, '--previous-snapshot', previous_snapshot_path, '--delta-out', delta_out_path]
    subprocess.run(cmd, check=True)

def run_sensitivity(input_path, config_path, output_path):
    cmd = [sys.executable, 'scripts/sensitivity.py', '--input', input_path, '--config', config_path, '--output', output_path]
    subprocess.run(cmd, check=True)

def run_generate_manifest(input_path, config_path, output_path, period, version):
    cmd = [sys.executable, 'scripts/generate_manifest.py', '--input', input_path, '--config', config_path, '--output', output_path, '--period', period, '--version', version]
    subprocess.run(cmd, check=True)

def main():
    # Example usage: update with actual argument parsing as pipeline expands
    input_path = 'data/raw/Vigilancia_Publicacions_2025_10.xlsx'
    cleaned_path = 'data/processed/Families_Clean_2025_10.xlsx'
    fit_index_path = 'data/processed/TRL2-4_Fit_Index_2025_10.xlsx'
    flags_path = 'data/processed/TRL2-4_Fit_Index_2025_10_internal.xlsx'
    missions_path = 'data/processed/TRL2-4_Fit_Index_2025_10_internal.xlsx'  # Overwrite with mapped columns
    public_path = 'data/processed/TRL2-4_Fit_Index_2025_10_public.csv'
    figures_dir = 'data/figures/2025_10'
    previous_snapshot_path = 'data/history/2025_09.xlsx'
    delta_out_path = 'data/processed/monthly_update_2025_10.xlsx'
    sensitivity_out_path = 'data/processed/sensitivity_2025_10.xlsx'
    manifest_path = 'logs/run_manifest_2025_10.json'
    config_path = 'config.yaml'
    pipeline_version = '0.1.0'
    whitelist_path = 'data/lists/whitelist.csv'
    blacklist_path = 'data/lists/blacklist.csv'
    cpc_map_path = 'data/lists/cpc_to_mission.csv'
    run_parse_patents(input_path, cleaned_path, config_path)
    run_compute_fit_index(cleaned_path, fit_index_path, config_path)
    run_augment_flags(fit_index_path, flags_path, whitelist_path, blacklist_path, config_path)
    run_map_to_missions(flags_path, missions_path, cpc_map_path, config_path)
    run_export_views(missions_path, public_path, config_path)
    run_generate_charts(missions_path, '2025_10', figures_dir, config_path)
    run_delta_report(missions_path, previous_snapshot_path, delta_out_path)
    run_sensitivity(missions_path, config_path, sensitivity_out_path)
    run_generate_manifest(missions_path, config_path, manifest_path, '2025_10', pipeline_version)
    # End of pipeline

if __name__ == "__main__":
    main()
