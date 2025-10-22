# Runbook

## Instalación de dependencias

1. Instala Python 3.9+ si no lo tienes.
2. Instala las dependencias ejecutando:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución del pipeline

### 1. Parseo y limpieza de patentes

Puedes ejecutar el primer paso del pipeline (parseo y limpieza) usando el CLI:

```bash
python scripts/cli.py parse --input data/raw/Vigilancia_Publicacions_2025_10.xlsx --output data/processed/Families_Clean_2025_10.xlsx --config config.yaml
```

### 2. Ejecución completa del pipeline

```bash
python scripts/run_all.py
```

## Salidas principales

- Procesados: `data/processed/TRL2-4_Fit_Index_<YYYY_MM>_internal.xlsx`, `data/processed/TRL2-4_Fit_Index_<YYYY_MM>_public.csv`
- Gráficos: `data/figures/<YYYY_MM>/Radar_TRL_Fit_ABC.png`, `Top10_TRL_Fit_Index.png`, `Trend_Patents.png`
- Dashboard: `dashboard/Radar_Tecnologico_<YYYY_MM>.xlsx`
- Monthly Update: `data/processed/monthly_update_<YYYY_MM>.xlsx`
- Manifest: `logs/run_manifest_<YYYY_MM>.json`

## Estructura de carpetas

- `data/raw/`: Excel fuente mensual
- `data/processed/`: Archivos procesados
- `data/figures/`: Gráficos generados
- `data/history/`: Históricos y base agregada
- `data/lists/`: Tablas auxiliares (whitelist, blacklist, cpc_to_mission)
- `scripts/`: Scripts del pipeline
- `dashboard/`: Dashboard Excel
- `logs/`: Logs y manifiestos de ejecución
- `docs/`: Documentación

## Recomendaciones

- Mantén actualizada la lista de dependencias en `requirements.txt`.
- Usa entornos virtuales para aislar dependencias si lo prefieres.
