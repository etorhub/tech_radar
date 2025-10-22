# Radar Tecnológico de Patentes TRL2–4

Este repositorio implementa un pipeline completo para el procesamiento mensual de patentes, cálculo de TRL2–4 Fit, categorización tecnológica, generación de informes y dashboard, según los requisitos definidos inicialmente.

## Instalación

1. Clona el repositorio.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

- Ejecuta el pipeline completo:
  ```bash
  python scripts/run_all.py
  ```
- Ejecuta el parseo y limpieza de patentes:
  ```bash
  python scripts/cli.py parse --input data/raw/Vigilancia_Publicacions_2025_10.xlsx --output data/processed/Families_Clean_2025_10.xlsx --config config.yaml
  ```

## Documentación

- Consulta `docs/RUNBOOK.md` para instrucciones detalladas de uso.
- Consulta `docs/DATA_DICTIONARY.md` para el diccionario de datos.
