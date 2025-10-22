import argparse
import sys
import subprocess

# Placeholder for cli.py
# CLI alternative to run_all.py with subcommands.

def main():
    parser = argparse.ArgumentParser(description="Radar Tech Pipeline CLI")
    subparsers = parser.add_subparsers(dest='command')

    # Parse patents subcommand
    parse_parser = subparsers.add_parser('parse', help='Parse and clean patent Excel file')
    parse_parser.add_argument('--input', required=True, help='Input Excel file path')
    parse_parser.add_argument('--output', required=True, help='Output cleaned Excel file path')
    parse_parser.add_argument('--config', required=False, help='Config YAML path')

    # Compute fit index subcommand
    fit_parser = subparsers.add_parser('fit', help='Compute TRL2–4 Fit Index and assign categories')
    fit_parser.add_argument('--input', required=True, help='Input cleaned Excel file path')
    fit_parser.add_argument('--output', required=True, help='Output Excel file path')
    fit_parser.add_argument('--config', required=True, help='Config YAML path')

    # Augment flags subcommand
    flags_parser = subparsers.add_parser('flags', help='Apply Venture Builder flags and exclusion rules')
    flags_parser.add_argument('--input', required=True, help='Input Excel file path')
    flags_parser.add_argument('--output', required=True, help='Output Excel file path')
    flags_parser.add_argument('--whitelist', required=True, help='Whitelist CSV path')
    flags_parser.add_argument('--blacklist', required=True, help='Blacklist CSV path')
    flags_parser.add_argument('--config', required=True, help='Config YAML path')

    # Map to missions subcommand
    map_parser = subparsers.add_parser('map', help='Map CPC/IPC codes to tech domains and mission codes')
    map_parser.add_argument('--input', required=True, help='Input Excel file path')
    map_parser.add_argument('--output', required=True, help='Output Excel file path')
    map_parser.add_argument('--cpc-map', required=True, help='CPC/IPC map CSV path')
    map_parser.add_argument('--config', required=True, help='Config YAML path')

    # Export views subcommand
    export_parser = subparsers.add_parser('export', help='Export internal and public views from processed data')
    export_parser.add_argument('--input', required=True, help='Input processed Excel file path')
    export_parser.add_argument('--public', required=True, help='Output public CSV file path')
    export_parser.add_argument('--config', required=True, help='Config YAML path')

    # Generate charts subcommand
    charts_parser = subparsers.add_parser('charts', help='Generate charts from processed data')
    charts_parser.add_argument('--input', required=True, help='Input processed Excel file path')
    charts_parser.add_argument('--period', required=True, help='Period (YYYY_MM)')
    charts_parser.add_argument('--outdir', required=True, help='Output directory for figures')

    # Delta report subcommand
    delta_parser = subparsers.add_parser('delta', help='Generate Monthly Update delta report')
    delta_parser.add_argument('--current', required=True, help='Current processed Excel file path')
    delta_parser.add_argument('--previous-snapshot', required=True, help='Previous snapshot Excel file path')
    delta_parser.add_argument('--delta-out', required=True, help='Output Excel file path for delta report')

    # Sensitivity analysis subcommand
    sens_parser = subparsers.add_parser('sensitivity', help='Sensitivity analysis of TRL2–4 Fit Index weights')
    sens_parser.add_argument('--input', required=True, help='Input processed Excel file path')
    sens_parser.add_argument('--config', required=True, help='Config YAML path')
    sens_parser.add_argument('--output', required=True, help='Output Excel file path for sensitivity results')

    # Generate manifest subcommand
    manifest_parser = subparsers.add_parser('manifest', help='Generate pipeline run manifest')
    manifest_parser.add_argument('--input', required=True, help='Input processed Excel file path')
    manifest_parser.add_argument('--config', required=True, help='Config YAML path')
    manifest_parser.add_argument('--output', required=True, help='Output manifest JSON file path')
    manifest_parser.add_argument('--period', required=True, help='Period (YYYY_MM)')
    manifest_parser.add_argument('--version', required=True, help='Pipeline version string')

    args = parser.parse_args()

    if args.command == 'parse':
        cmd = [sys.executable, 'scripts/parse_patents.py', '--input', args.input, '--output', args.output]
        if args.config:
            cmd += ['--config', args.config]
        subprocess.run(cmd)
    elif args.command == 'fit':
        cmd = [sys.executable, 'scripts/compute_fit_index.py', '--input', args.input, '--output', args.output, '--config', args.config]
        subprocess.run(cmd)
    elif args.command == 'flags':
        cmd = [sys.executable, 'scripts/augment_flags.py', '--input', args.input, '--output', args.output, '--whitelist', args.whitelist, '--blacklist', args.blacklist, '--config', args.config]
        subprocess.run(cmd)
    elif args.command == 'map':
        cmd = [sys.executable, 'scripts/map_to_missions.py', '--input', args.input, '--output', args.output, '--cpc-map', args.cpc_map, '--config', args.config]
        subprocess.run(cmd)
    elif args.command == 'export':
        cmd = [sys.executable, 'scripts/export_views.py', '--input', args.input, '--public', args.public, '--config', args.config]
        subprocess.run(cmd)
    elif args.command == 'charts':
        cmd = [sys.executable, 'scripts/generate_charts.py', '--input', args.input, '--period', args.period, '--outdir', args.outdir]
        subprocess.run(cmd)
    elif args.command == 'delta':
        cmd = [sys.executable, 'scripts/delta_report.py', '--current', args.current, '--previous-snapshot', args.previous_snapshot, '--delta-out', args.delta_out]
        subprocess.run(cmd)
    elif args.command == 'sensitivity':
        cmd = [sys.executable, 'scripts/sensitivity.py', '--input', args.input, '--config', args.config, '--output', args.output]
        subprocess.run(cmd)
    elif args.command == 'manifest':
        cmd = [sys.executable, 'scripts/generate_manifest.py', '--input', args.input, '--config', args.config, '--output', args.output, '--period', args.period, '--version', args.version]
        subprocess.run(cmd)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
