# 03 — Agenda como tools

Objetivo: permitir que el modelo decida cuándo buscar sesiones y cuándo pedir
los detalles de una charla.

```bash
python agent.py "¿Qué charlas presenciales de seguridad hay el viernes?"
python agent.py "Contame de la charla de Rob Pike"
```

Conceptos:

- decorador `@tool`;
- docstrings como contrato para el modelo;
- agent loop;
- resultados estructurados y acotados;
- contenido externo tratado como datos no confiables.

El agente no recibe las 135 charlas dentro del prompt. Consulta solamente lo
que necesita, evitando gastar contexto y reduciendo respuestas inventadas.
