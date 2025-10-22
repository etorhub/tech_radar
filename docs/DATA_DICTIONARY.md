# Diccionario de Datos

## Campos principales procesados en el pipeline

- **Assignee Details Name**: Titulares de la patente, normalizados y deduplicados.
- **Patent Number**: Número de patente principal.
- **Patent Number2**: Número alternativo o ID de familia (si existe).
- **Publication Date**: Fecha de publicación (formato YYYY-MM-DD, primera fecha válida).
- **Title**: Título de la patente.
- **Patent Valuation Score Technology**: Score tecnológico (extraído como porcentaje).
- **Patent Valuation Score Legal**: Score legal (extraído como porcentaje).
- **Patent Valuation Score Citation**: Score de citaciones (extraído como porcentaje).
- **Country Code**: Países asociados a la familia de patentes.
- **Family_Size**: Número de miembros en la familia deduplicada.
- **family_key**: Clave única de familia (por Patent Number2 o heurística).
- **TRL_Fit_Index**: Índice calculado y normalizado (0–100).
- **TRL_Category**: Categoría A/B/C según umbrales.
- **VB_Eligible**: Flag de elegibilidad Venture Builder.
- **Primary_Domain**: Dominio tecnológico principal.
- **Primary_Mission**: Misión principal (M1–M8, M0 si no mapeado).
- **Domain_Weights_JSON**: Asignación fraccionada de dominios.
- **Mapping_Method**: CPC, KEYWORD, UNMAPPED.
