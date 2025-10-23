import subprocess
import sys
import os

# Placeholder for run_all.py
# Orchestrates the monthly pipeline execution.


def run_parse_patents(input_path, output_path, config_path=None):
    cmd = [
        sys.executable,
        "scripts/parse_patents.py",
        "--input",
        input_path,
        "--output",
        output_path,
    ]
    if config_path:
        cmd += ["--config", config_path]
        print(
            f"Executant parse_patents amb entrada: {input_path} i sortida: {output_path}"
        )
        subprocess.run(cmd, check=True)


def run_compute_fit_index(input_path, output_path, config_path):
    cmd = [
        sys.executable,
        "scripts/compute_fit_index.py",
        "--input",
        input_path,
        "--output",
        output_path,
        "--config",
        config_path,
    ]
    print(
        f"Executant compute_fit_index amb entrada: {input_path} i sortida: {output_path}"
    )
    subprocess.run(cmd, check=True)


def run_augment_flags(
    input_path, output_path, whitelist_path, blacklist_path, config_path
):
    cmd = [
        sys.executable,
        "scripts/augment_flags.py",
        "--input",
        input_path,
        "--output",
        output_path,
        "--whitelist",
        whitelist_path,
        "--blacklist",
        blacklist_path,
        "--config",
        config_path,
    ]
    print(
        f"Executant augment_flags amb entrada: {input_path}, sortida: {output_path}, whitelist: {whitelist_path}, blacklist: {blacklist_path}"
    )
    subprocess.run(cmd, check=True)


def run_map_to_missions(input_path, output_path, cpc_map_path, config_path):
    cmd = [
        sys.executable,
        "scripts/map_to_missions.py",
        "--input",
        input_path,
        "--output",
        output_path,
        "--cpc-map",
        cpc_map_path,
        "--config",
        config_path,
    ]
    print(
        f"Executant map_to_missions amb entrada: {input_path}, sortida: {output_path}, cpc_map: {cpc_map_path}"
    )
    subprocess.run(cmd, check=True)


def run_export_views(input_path, public_path, config_path):
    cmd = [
        sys.executable,
        "scripts/export_views.py",
        "--input",
        input_path,
        "--public",
        public_path,
        "--config",
        config_path,
    ]
    print(
        f"Executant export_views amb entrada: {input_path}, sortida pública: {public_path}"
    )
    subprocess.run(cmd, check=True)


def run_generate_charts(input_path, period, outdir, config_path):
    cmd = [
        sys.executable,
        "scripts/generate_charts.py",
        "--input",
        input_path,
        "--period",
        period,
        "--outdir",
        outdir,
        "--config",
        config_path,
    ]
    print(
        f"Executant generate_charts amb entrada: {input_path}, període: {period}, directori: {outdir}"
    )
    subprocess.run(cmd, check=True)


def run_delta_report(current_path, previous_snapshot_path, delta_out_path):
    cmd = [
        sys.executable,
        "scripts/delta_report.py",
        "--current",
        current_path,
        "--previous-snapshot",
        previous_snapshot_path,
        "--delta-out",
        delta_out_path,
    ]
    print(
        f"Executant delta_report amb actual: {current_path}, anterior: {previous_snapshot_path}, sortida: {delta_out_path}"
    )
    subprocess.run(cmd, check=True)


def run_sensitivity(input_path, config_path, output_path):
    cmd = [
        sys.executable,
        "scripts/sensitivity.py",
        "--input",
        input_path,
        "--config",
        config_path,
        "--output",
        output_path,
    ]
    print(f"Executant sensitivity amb entrada: {input_path}, sortida: {output_path}")
    subprocess.run(cmd, check=True)


def run_generate_manifest(input_path, config_path, output_path, period, version):
    cmd = [
        sys.executable,
        "scripts/generate_manifest.py",
        "--input",
        input_path,
        "--config",
        config_path,
        "--output",
        output_path,
        "--period",
        period,
        "--version",
        version,
    ]
    print(
        f"Executant generate_manifest amb entrada: {input_path}, període: {period}, versió: {version}, sortida: {output_path}"
    )
    subprocess.run(cmd, check=True)


def main():
    import argparse
    import yaml

    parser = argparse.ArgumentParser(description="Run the monthly pipeline.")
    parser.add_argument("--input", required=True, help="Input Excel file (.xlsx)")
    parser.add_argument("--period", required=True, help="Period string, e.g. 2025_10")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    args = parser.parse_args()

    # Load config
    with open(args.config, "r") as f:
        config = yaml.safe_load(f)

    period = args.period
    input_path = args.input

    # Paths are constructed using period
    cleaned_path = f"data/processed/Families_Clean_{period}.xlsx"
    fit_index_path = f"data/processed/TRL2-4_Fit_Index_{period}.xlsx"
    flags_path = f"data/processed/TRL2-4_Fit_Index_{period}_internal.xlsx"
    missions_path = f"data/processed/TRL2-4_Fit_Index_{period}_internal.xlsx"
    public_path = f"data/processed/TRL2-4_Fit_Index_{period}_public.csv"
    figures_dir = f"data/figures/{period}"
    previous_snapshot_path = config.get(
        "previous_snapshot_path", f"data/history/{period}_prev.xlsx"
    )
    delta_out_path = f"data/processed/monthly_update_{period}.xlsx"
    sensitivity_out_path = f"data/processed/sensitivity_{period}.xlsx"
    manifest_path = f"logs/run_manifest_{period}.json"
    pipeline_version = config.get("pipeline_version", "0.1.0")
    whitelist_path = config.get("whitelist_path", "data/lists/whitelist.csv")
    blacklist_path = config.get("blacklist_path", "data/lists/blacklist.csv")
    cpc_map_path = config.get("cpc_map_path", "data/lists/cpc_to_mission.csv")

    run_parse_patents(input_path, cleaned_path, args.config)
    run_compute_fit_index(cleaned_path, fit_index_path, args.config)
    run_augment_flags(
        fit_index_path, flags_path, whitelist_path, blacklist_path, args.config
    )
    run_map_to_missions(flags_path, missions_path, cpc_map_path, args.config)
    run_export_views(missions_path, public_path, args.config)
    run_generate_charts(missions_path, period, figures_dir, args.config)
    run_delta_report(missions_path, previous_snapshot_path, delta_out_path)
    run_sensitivity(missions_path, args.config, sensitivity_out_path)
    run_generate_manifest(
        missions_path, args.config, manifest_path, period, pipeline_version
    )
    # End of pipeline


if __name__ == "__main__":
    main()
