# Radar Tecnológico de Patentes TRL2–4

## Descripción

Pipeline reproducible para procesar, analizar y visualizar datos de patentes TRL2–4. Incluye parseo, deduplicación, cálculo de índices, categorización, generación de gráficos, dashboard en Excel, y trazabilidad.

## Estructura principal

- `data/raw/`: Excel fuente mensual
- `data/processed/`: Archivos procesados
- `data/figures/`: Gráficos generados
- `data/history/`: Históricos y base agregada
- `data/lists/`: Tablas auxiliares (whitelist, blacklist, cpc_to_mission)
- `scripts/`: Scripts del pipeline
- `dashboard/`: Dashboard Excel
- `logs/`: Logs y manifiestos de ejecución
- `docs/`: Documentación

## Ejecución rápida

1. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta el pipeline completo:
   ```bash
   python scripts/run_all.py
   ```
3. El dashboard Excel se genera automáticamente en `dashboard/Radar_Tecnologico_<YYYY_MM>.xlsx`.

## Documentación adicional

- Consulta `docs/DATA_DICTIONARY.md` para campos y reglas de datos.
- Consulta `docs/RUNBOOK.md` para instrucciones detalladas de uso.
