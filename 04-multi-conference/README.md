# 04 — Multi-conferencia

Objetivo: soportar múltiples conferencias con un único agente. La
implementación inicial cubre Nerdearla Argentina 2026 (checkpoint 02–03)
y KubeCon + CloudNativeCon North America 2026.

## Estructura

- `sessionize_adapter.py`: normaliza los payloads de Sessionize al modelo
  interno (mismo formato que `02-schedule-data/schedule.py`).
- `refresh_sessionize.py`: descarga el snapshot de Sessionize a
  `data/kubecon-na-2026.json`. Soporta `--check-only` para validar sin red.
- `conference_data.py`: API común para listar, cargar y buscar sesiones en
  cualquier conferencia soportada.
- `agent.py`: agente Strands con tools unificadas y dos modos de uso.

## Uso

```bash
# Descargar el snapshot de KubeCon (sólo cuando la API esté disponible)
python 04-multi-conference/refresh_sessionize.py

# Validar el snapshot sin red
python 04-multi-conference/refresh_sessionize.py --check-only

# Pregunta única (compatible con 01–03)
python 04-multi-conference/agent.py \
  "¿qué charlas de seguridad hay el viernes en KubeCon?"

# Modo chat interactivo
python 04-multi-conference/agent.py --chat
```

## Comandos del modo chat

- `/conferences` — lista las conferencias soportadas.
- `/clear` — reinicia la conversación.
- `/help` — muestra la ayuda.
- `exit`, `quit`, `Ctrl+C` o `Ctrl+D` — sale del REPL.

## Tools expuestas al agente

- `search_conference_sessions(query, day, track, session_type, conference)`:
  busca sesiones; `conference` vacío busca en todas.
- `get_conference_session(session_id)`: devuelve detalles completos. El
  prefijo del ID identifica la conferencia.
- `list_supported_conferences()`: devuelve la lista de conferencias
  soportadas.

## Adaptadores disponibles

| Conferencia | ID | Fuente de datos |
| --- | --- | --- |
| Nerdearla Argentina 2026 | `nerdearla` | API de Backstage de Nerdearla |
| KubeCon + CloudNativeCon NA 2026 | `kubecon-na-2026` | API interna de la PWA de Sessionize |

## Notas

- Los snapshots son JSON versionados en `data/`. El agente no hace llamadas
  de red en tiempo de ejecución.
- El endpoint `/api/schedule` de Sessionize devuelve 391+ sesiones y la
  metadata de categorías. No incluye speakers ni rooms con datos
  enriquecidos: las speakers llegan como IDs. Se usa el nombre de la
  categoría como `track`.
- El timezone de KubeCon es `America/Denver`. Los horarios están en hora
  local del evento (Mountain Standard Time).
- La sesión `1244695` ("When the Agent Lost Its Patience") se usa como
  fixture de tests para verificar normalización y búsqueda.
