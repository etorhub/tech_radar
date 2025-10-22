# Proyecto: Radar Tecnológico de Patentes TRL2–4 The Collider

## Pipeline de ejecución mensual

### 0. Contexto

Partimos de un Excel mensual tipo `Vigilancia_Publicacions_<periodo>.xlsx` (hoja Families). Necesitamos un pipeline reproducible que:

1. Parsee/limpie el Excel mensual con QA.
2. Deduzca familias (dedupe) y normalice titulares.
3. Calcule el TRL2–4 Fit Index y categorías A/B/C.
4. Aplique flags VB (excluir co-propiedad con empresas, etc.).
5. Mapee a Misiones País (CPC/IPC → dominio → misión).
6. Genere salidas internas y públicas + gráficos + dashboard.
7. Mantenga histórico agregado y produzca un Monthly Update (delta vs mes anterior).
8. Deje trazabilidad, logs y configuración en `config.yaml`.

**Requisito clave:** cada mes que entren ficheros, se amplía la base agregada y se publica Monthly Update (altas/bajas/cambios).

**Importante:** Scripts basados en Python y librerías disponibles, sin uso de llamadas a sistemas de inteligencia artificial.

---

## 1. Entregables

### 1.1 Scripts

- `scripts/parse_patents.py` — limpieza, normalización, fechas, dedupe por familia.
- `scripts/compute_fit_index.py` — TRL2–4 Fit + categorías A/B/C.
- `scripts/augment_flags.py` — flags VB (empresa co-propiedad, whitelist/blacklist, estado legal).
- `scripts/map_to_missions.py` — mapeo CPC/IPC → Dominio → Mission_Code.
- `scripts/export_views.py` — interna.xlsx (completa) y public.csv (agregada/anónima).
- `scripts/generate_charts.py` — radar A/B/C, top10, tendencia mensual.
- `scripts/delta_report.py` — Monthly Update: NEW/DROPPED/UPGRADED/DOWNGRADED/EXCLUDED_BY_RULE.
- `scripts/run_all.py` — orquestador mensual (todas las fases).
- `scripts/sensitivity.py` — análisis de sensibilidad de pesos (opcional, recomendado).
- `scripts/cli.py` — alternativa a run_all.py con subcomandos.

### 1.2 Configuración y tablas auxiliares

- `config.yaml` — pesos, umbrales, reglas VB, rutas, versiones.
- `data/lists/cpc_to_mission.csv` — mapeo CPC/IPC → dominio → misión (con confidence).
- `data/lists/whitelist.csv` — centros/fundaciones permitidos (no contar como empresa).
- `data/lists/blacklist.csv` — empresas a excluir explícitamente (si aplica).
- `data/lists/keywords_to_domain.csv` — (opcional) fallback por palabras clave controladas.

### 1.3 Salidas mensuales (por periodo `<YYYY_MM>`)

- **Procesados**
  - `data/processed/TRL2-4_Fit_Index_<YYYY_MM>_internal.xlsx`
  - `data/processed/TRL2-4_Fit_Index_<YYYY_MM>_public.csv`
- **Gráficos**
  - `data/figures/<YYYY_MM>/Radar_TRL_Fit_ABC.png`
  - `data/figures/<YYYY_MM>/Top10_TRL_Fit_Index.png`
  - `data/figures/<YYYY_MM>/Trend_Patents.png`
- **Histórico agregado**
  - `data/history/<YYYY_MM>.parquet` (snapshot mensual)
  - Base agregada: `data/history/base_agg.parquet` (se actualiza concatenando y deduplicando por familia)
- **Monthly Update**
  - `data/processed/monthly_update_<YYYY_MM>.xlsx` con pestañas: NEW, DROPPED, UPGRADED, DOWNGRADED, EXCLUDED_BY_RULE.
- **Trazabilidad**
  - `logs/run_manifest_<YYYY_MM>.json` (hash input, versión pipeline, recuentos, % mapeo, tiempos por etapa).

### 1.4 Dashboard

- `dashboard/Radar_Tecnologico.pbix` (o .xlsx) con: Overview, Radar TRL-Fit, Spin-off Candidates (A), Heatmap por Misión/Mes, Pareto por titular, Cohorts, Delta.
- Heatmap ponderado por Domain_Weights (no solo por conteo entero).
- Coverage KPI: card con %M0 del mes y Top-5 CPC sin regla.

---

## 2. Requisitos funcionales

### 2.1 Parsing, limpieza y QA

- Detectar columnas clave (nombres pueden variar ligeramente):
  - Assignee Details Name, Patent Number, Patent Number2, Publication Date, Application Date,
  - Patent Valuation Score Overall/Citation/Technology/Legal/Commercial,
  - Country Code, Dead or Alive, Litigation Exists, 1st Main Claim, Title.
- Fechas: si hay múltiples valores en celda, tomar la primera en formato YYYY-MM-DD.
- Porcentajes: extraer el último % visible para cada Valuation Score … y convertir a float (0–100).
- Titulares: dividir por saltos de línea, normalizar (mayúsculas, sin acentos, sin símbolos) y de-duplicar por fila.
- Deduplicación por familia:
  - Preferir Patent Number2 o ID de familia si existe.
  - Si no, heurística: `family_key = normalize(Title) + '|' + PublicationDate`.
  - Agregados por familia:
    - Score\_\* = media,
    - Country Code = conjunto,
    - Assignees = conjunto,
    - Publication Date = más reciente,
    - Family_Size = nº de miembros.
- QA:
  - Validación de esquema (tipos y rangos).
  - `QA_report.xlsx` con filas anómalas.
  - Interrumpir ejecución si faltan columnas obligatorias.

### 2.2 Cálculo TRL2–4 Fit (0–100)

- Variables:
  - Score_Technology, Score_Legal, Score_Citation (0–100);
  - Freshness Flag = 1 si PublicationDate ≤ 36 meses;
  - PCT Flag = 1 si Patent Number contiene WO.
  - Technology_Norm = Score_Technology / max(Score_Technology_en_periodo) \* 100.
- Índice (antes de normalizar):
  - `TRL_Fit_Index_raw = 0.40 * Technology_Norm + 0.15 * Score_Legal + 0.10 * Score_Citation + 0.10 * (Freshness Flag * 100) + 0.05 * (PCT Flag * 100)`
- Normalizar TRL_Fit_Index a 0–100 respecto al máximo del periodo.
- Categorías:
  - A (High) > 66
  - B (Medium) 33–66
  - C (Low) ≤ 33

### 2.3 Flags Venture Builder (VB) y reglas

- Industry_CoOwner_Flag = 1 si cualquier cotitular parece empresa (regex formas jurídicas: SL/SA/SLU/SLL, GmbH, Ltd, LLC, Inc, Corp, SAS, BV, AG, PLC, SPA, etc.).
  - Aplicar whitelist (centros/fundaciones): si matchea whitelist, no se marca como empresa.
- Alive_Flag y Litigation_Flag si las columnas existen.
- VB_Eligible = 1 si:
  - Industry_CoOwner_Flag == 0
  - Freshness Flag == 1
  - (opcional) Alive_Flag == 1
  - (opcional) Litigation_Flag == 0
- VB_Exclusion_Reason (string, primera que aplique en orden jerárquico):
  - company_coprop, stale_ip, dead, litigation, other.
- VB_Override (include/exclude) y VB_Override_Reason —el pipeline respeta overrides.

### 2.4 Categorización tecnológica semi-automática (sin IA)

**Objetivo:** Asignar a cada patente/familia un Dominio Tecnológico y Mission_Code de forma determinística y auditable, usando principalmente Códigos CPC/IPC y, en ausencia de estos, un fallback de palabras clave gobernado por listas.

#### 2.4.1 Entradas

- Campos por patente/familia:
  - CPC/IPC Codes (lista de códigos por fila; si vienen concatenados, se normalizan y separan).
- Tablas gobernadas (editables):
  - `data/lists/cpc_to_mission.csv` con columnas:
    - prefix (p. ej., C12N, C12N15, H04W, A61K, G06F16)
    - tech_domain (p. ej., “Biotech – Ingeniería genética”, “Telecom – Redes”)
    - mission_code (M1…M8; usar M0 para “no mapeado”)
    - confidence (1–100; mayor = más confiable)
    - notes (opcional)
  - (Opcional) `data/lists/keywords_to_domain.csv` con columnas:
    - keyword, tech_domain, mission_code, confidence, notes

#### 2.4.2 Reglas de decisión (prioridad)

1. Match por CPC/IPC (sin texto libre):
   - Para cada código de la patente, buscar todas las reglas cuyo prefix sea prefijo del código (startswith).
   - Si varias reglas coinciden, escoger la de mayor confidence; en empate, el prefijo más largo (mayor especificidad).
2. Fallback por keywords (solo si no hay match CPC/IPC):
   - Buscar coincidencias exactas/normalizadas en keywords_to_domain.csv.
   - Misma prioridad: mayor confidence, luego keyword más específica (longitud).
3. Sin coincidencias: asignar Mission_Code = M0 (Unmapped).

Todas las reglas son determinísticas y están externas al código (CSV), para que el equipo las mantenga sin tocar Python.

#### 2.4.3 Asignación primaria y fraccionada

- Dominio/Misión primario: el resultante de la regla con mayor confidence; si empata, el de prefijo más largo; si persiste, criterio secundario del config.yaml (p. ej., prioridad por misión).
- Asignación fraccionada (recomendada): si la familia tiene varios códigos que mapean a distintos dominios, repartir peso uniforme (o ponderado por profundidad del prefijo) entre ellos:
  - Domain_Weights (diccionario): suma 1.0 por fila.
  - Permite análisis agregados fieles (una familia puede tocar 2–3 dominios).

#### 2.4.4 Salidas por fila (nuevas columnas)

- Primary_Domain (string)
- Primary_Mission (M1…M8, M0 si no mapeado)
- Domain_Weights_JSON (JSON con {dominio: peso, …} que suma 1.0)
- Matched_Prefixes (lista/“;”-join de prefijos aplicados)
- Mapping_Method (CPC, KEYWORD, UNMAPPED)

#### 2.4.5 KPIs y QA de categorización

- Cobertura de mapeo: % Mapeado = 1 − %M0.
  - Umbral configurable (p. ej., ≥ 90%). Si se incumple, WARNING en run*manifest*<YYYY_MM>.json.
- Reporte de huecos: top-20 CPC/IPC sin regla (para que el equipo actualice cpc_to_mission.csv).
- Determinismo: mismo input + mismas reglas ⇒ mismas salidas (verificado en test E2E).

#### 2.4.6 Ejemplos de tablas gobernadas

**data/lists/cpc_to_mission.csv**

```csv
prefix,tech_domain,mission_code,confidence,notes
C12N,Biotech – Ingeniería genética,M4,95,Genética/biotecnología (general)
C12N15,Biotech – Terapias génicas,M4,98,Terapia génica (específico)
H04W,Telecom – Redes móviles,M2,92,Gestión/seguridad redes
G06F16,Digital – Gestión de datos,M3,90,Indexación/consulta de datos
A61K,Salud – Formulaciones,M1,90,Fármacos/composiciones
```

**(Opcional) data/lists/keywords_to_domain.csv**

```csv
keyword,tech_domain,mission_code,confidence,notes
thermoelectric,Energía – Termoeléctrica,M5,80,Materiales termoeléctricos
graphene,Materiales – 2D,M6,75,Materiales bidimensionales
```

#### 2.4.7 Integración en el pipeline

- Script: `scripts/map_to_missions.py`
  - Input: Excel/Parquet ya normalizado (tras augment_flags.py).
  - Output: mismo fichero con las columnas nuevas de mapeo.
  - CLI (ya definido en 3.1):
  ```bash
  python scripts/map_to_missions.py \
    --input data/processed/TRL2-4_Fit_Index_<YYYY_MM>_internal.xlsx \
    --cpc-map data/lists/cpc_to_mission.csv \
    --keywords-map data/lists/keywords_to_domain.csv \
    --output data/processed/TRL2-4_Fit_Index_<YYYY_MM>_internal.xlsx
  ```
- Config (añadir a config.yaml):

```yaml
mapping:
  use_fractional_assignment: true
  prefer_deeper_prefix_on_ties: true
  coverage_warning_threshold_pct_m0: 10 # alerta si >10% sin mapear
  fallback_keywords_enabled: true
paths:
  cpc_map: 'data/lists/cpc_to_mission.csv'
  keywords_map: 'data/lists/keywords_to_domain.csv'
```

### 2.4 Mapeo CPC/IPC → Dominio → Misiones País

- Input: cpc_to_mission.csv con columnas prefix;tech_domain;mission_code;confidence.
- Asignar por startswith(prefix) el mapeo con mayor confidence; si no hay coincidencia: Mission_Code = M0 (Unmapped).
- Reportar en el manifest el % sin mapear (M0).

### 2.5 Salidas (interna y pública)

- Interna (`…_internal.xlsx`): todas las columnas, incluidas razones de exclusión y overrides.
- Pública (`…_public.csv`): agregada por Month x Tech_Domain x Mission_Code:
  - families_count, %PCT, distribución A/B/C, avg_Technology.
  - No incluir Patent Number, Assignee, Title, Abstract.

### 2.6 Históricos, base agregada y Monthly Update

- Snapshot mensual: guardar `data/history/<YYYY_MM>.parquet`.
- Base agregada: actualizar `data/history/base_agg.parquet` concatenando snapshots y deduplicando por familia (usar family_key o Patent Number2).
- Monthly Update (`delta_report.py`):
  - NEW: familias en `<YYYY_MM>` que no estaban en `<YYYY_MM-1>`.
  - DROPPED: familias que estaban en `<YYYY_MM-1>` y no en `<YYYY_MM>`.
  - UPGRADED: cambio de categoría B→A o C→A.
  - DOWNGRADED: A→B/C o B→C.
  - EXCLUDED_BY_RULE: casos que pasan a no elegibles por nuevas reglas (empresa, stale, etc.).
  - Entrega: `monthly_update_<YYYY_MM>.xlsx` con pestañas por categoría y un README breve dentro.

### 2.7 Gráficos

- `Radar_TRL_Fit_ABC.png` — promedios A/B/C en Technology, Legal, Citation.
- `Top10_TRL_Fit_Index.png` — barras horizontales.
- `Trend_Patents.png` — serie mensual de familias (fecha de publicación).

---

## 3. Orquestación (CLI) y configuración

### 3.1 Comandos

```bash
# 1) Parse + clean + dedupe
python scripts/parse_patents.py \
  --input data/raw/Vigilancia_Publicacions_2025_10.xlsx \
  --output data/processed/Families_Clean_2025_10.xlsx \
  --config config.yaml

# 2) Compute TRL2–4 Fit
python scripts/compute_fit_index.py \
  --input data/processed/Families_Clean_2025_10.xlsx \
  --output data/processed/TRL2-4_Fit_Index_2025_10.xlsx \
  --config config.yaml

# 3) Flags VB
python scripts/augment_flags.py \
  --input data/processed/TRL2-4_Fit_Index_2025_10.xlsx \
  --src data/raw/Vigilancia_Publicacions_2025_10.xlsx \
  --output data/processed/TRL2-4_Fit_Index_2025_10_internal.xlsx \
  --whitelist data/lists/whitelist.csv \
  --blacklist data/lists/blacklist.csv \
  --config config.yaml

# 4) Mapeo a Misiones
python scripts/map_to_missions.py \
  --input data/processed/TRL2-4_Fit_Index_2025_10_internal.xlsx \
  --cpc-map data/lists/cpc_to_mission.csv \
  --output data/processed/TRL2-4_Fit_Index_2025_10_internal.xlsx

# 5) Vistas interna/pública
python scripts/export_views.py \
  --input data/processed/TRL2-4_Fit_Index_2025_10_internal.xlsx \
  --public data/processed/TRL2-4_Fit_Index_2025_10_public.csv \
  --config config.yaml

# 6) Figuras
python scripts/generate_charts.py \
  --input data/processed/TRL2-4_Fit_Index_2025_10_internal.xlsx \
  --period 2025_10 \
  --outdir data/figures/2025_10

# 7) Históricos y base agregada + Monthly Update
python scripts/delta_report.py \
  --current data/processed/TRL2-4_Fit_Index_2025_10_internal.xlsx \
  --previous-snapshot data/history/2025_09.parquet \
  --write-snapshot data/history/2025_10.parquet \
  --update-agg data/history/base_agg.parquet \
  --delta-out data/processed/monthly_update_2025_10.xlsx

# 8) Orquestador mensual (todo)
python scripts/run_all.py \
  --input data/raw/Vigilancia_Publicacions_2025_10.xlsx \
  --period 2025_10 \
  --config config.yaml
```

### 3.2 config.yaml (ejemplo mínimo)

```yaml
version: '1.0.0'
weights:
  technology: 0.40
  legal: 0.15
  citation: 0.10
  freshness: 0.10
  pct: 0.05

thresholds:
  freshness_months: 36
  a_cut: 66
  b_cut: 33

eligibility:
  exclude_company_coprop: true
  require_alive: true
  exclude_litigation: true
  allow_override: true

paths:
  whitelist: 'data/lists/whitelist.csv'
  blacklist: 'data/lists/blacklist.csv'
  cpc_map: 'data/lists/cpc_to_mission.csv'

missions:
  pct_required_missions: ['M2', 'M3'] # si aplican reglas específicas por misión
```

---

## 4. Estructura de carpetas

```
/radar_tech/
├── data/
│   ├── raw/                                   # Excel fuente mensual
│   ├── processed/
│   ├── figures/<YYYY_MM>/
│   ├── history/                               # snapshots parquet y base agregada
│   └── lists/                                 # whitelist.csv, blacklist.csv, cpc_to_mission.csv
├── scripts/
│   ├── parse_patents.py
│   ├── compute_fit_index.py
│   ├── augment_flags.py
│   ├── map_to_missions.py
│   ├── export_views.py
│   ├── generate_charts.py
│   ├── delta_report.py
│   ├── sensitivity.py
│   ├── run_all.py
│   └── cli.py
├── dashboard/
│   └── Radar_Tecnologico.pbix (o .xlsx)
├── logs/
│   └── run_manifest_<YYYY_MM>.json
├── config.yaml
└── docs/
    ├── README.md
    ├── DATA_DICTIONARY.md
    ├── RUNBOOK.md
    └── CHANGELOG.md
```

---

## 5. Criterios de aceptación (QA / Done)

1. Parsing/QA:
   - Fechas múltiples → se toma la primera válida.
   - Scores % extraídos correctamente.
   - Titulares normalizados y todos los cotitulares capturados.
   - QA_report.xlsx si hay anomalías.
2. Familias/Dedupe:
   - Uso de Patent Number2 si existe; si no, family_key heurístico.
   - Family_Size y agregados correctos.
3. TRL2–4 Fit:
   - Índice 0–100 normalizado; categorías correctas según config.yaml.
   - Technology_Norm respecto al máximo del periodo.
4. Flags VB:
   - Industry_CoOwner_Flag correcto (regex + whitelist).
   - VB_Eligible, VB_Exclusion_Reason, VB_Override aplicados y auditables.
5. Misiones País/Categorizacion:
   - Tech_Domain, Mission_Code asignados para ≥X% del dataset; %M0 reportado en manifest.
   - Primary_Domain, Primary_Mission, Domain_Weights_JSON, Matched_Prefixes, Mapping_Method generados por fila.
   - %M0 ≤ umbral (configurable); si se excede, WARNING en run_manifest.
   - Reporte de huecos: lista de CPC/IPC frecuentes sin regla en el periodo.
6. Salidas:
   - \_internal.xlsx con todas las columnas y motivos.
   - \_public.csv sin datos sensibles, con agregados correctos.
7. Monthly Update:
   - monthly*update*<YYYY_MM>.xlsx con pestañas NEW/DROPPED/UPGRADED/DOWNGRADED/EXCLUDED_BY_RULE.
   - Base agregada actualizada (base_agg.parquet).
8. Gráficos:
   - Tres PNG generados sin error para el periodo.
9. Trazabilidad:
   - run*manifest*<YYYY_MM>.json con: hash del input, versión pipeline, parámetros config.yaml, recuentos por filtro, %M0, nº A/B/C, nº VB elegibles, tiempos por etapa.
10. Documentación:
    - README.md, DATA_DICTIONARY.md, RUNBOOK.md, CHANGELOG.md entregados.
