# 02 — Datos de la agenda

Objetivo: incorporar datos externos antes de convertirlos en tools.

La API de Nerdearla devuelve todas las sesiones de una edición. Este
checkpoint permite actualizar el snapshot y hacer consultas deterministas sin
usar todavía un LLM.

```bash
python schedule.py stats
python schedule.py search --query kubernetes --day 2026-09-25
python schedule.py search --track SECURITY --type In-person
python refresh_schedule.py
```

Variables opcionales:

- `NERDEARLA_EVENT_ID`: ID de la edición.
- `NERDEARLA_API_URL`: endpoint completo alternativo.

Conceptos:

- fuentes externas;
- validación y normalización;
- snapshot offline;
- separación entre datos y razonamiento del modelo.
