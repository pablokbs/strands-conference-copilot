# Nerdearla Conference Copilot con Strands

[English version](README.en.md)

Tutorial progresivo para aprender
[Strands Agents SDK](https://strandsagents.com/) construyendo un agente que
ayuda a organizar la agenda de Nerdearla Argentina 2026.

La idea es que cada asistente pueda descargar el proyecto antes del workshop,
conectar un modelo y ejecutar cada etapa sin tener que copiar grandes bloques
de código durante la charla.

## Qué vamos a construir

El resultado final podrá:

- buscar charlas por tema, track, fecha y horario;
- recomendar una agenda personal sin superposiciones;
- recordar intereses y sesiones elegidas;
- guardar notas durante las charlas;
- resumir lo aprendido al final del día.

La agenda proviene de la API pública usada por Nerdearla. El repositorio
incluye además un snapshot para que el workshop continúe aunque el Wi-Fi del
evento decida convertirse en una experiencia de resiliencia distribuida.

## Progresión

| Etapa | Concepto | Estado |
| --- | --- | --- |
| [`01-hello-agent`](01-hello-agent/) | Primer agente y model provider | Ejecutable |
| [`02-schedule-data`](02-schedule-data/) | Datos externos y normalización | Ejecutable |
| [`03-schedule-tools`](03-schedule-tools/) | Custom tools y agent loop | Ejecutable |

Cada directorio representa un checkpoint y reutiliza el código de las etapas
anteriores. Se puede empezar desde cero o saltar a una etapa si el tiempo del
workshop se complica, siempre descargando el repositorio completo.

## Requisitos

- Python 3.10 o superior.
- Una cuenta AWS con acceso a Amazon Bedrock, **o** Ollama local.
- Git.

## Instalación

```bash
git clone https://github.com/pablokbs/strands-conference-copilot.git
cd strands-conference-copilot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Opción A: Amazon Bedrock

Configurá credenciales AWS usando el mecanismo habitual de AWS CLI:

```bash
aws configure
aws sts get-caller-identity
```

Después seleccioná región y modelo. El modelo debe estar habilitado en tu
cuenta de Bedrock.

```bash
export MODEL_PROVIDER=bedrock
export AWS_REGION=us-west-2
export BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
```

No guardes access keys en este repositorio ni en archivos `.env` versionados.

## Opción B: Ollama

Instalá Ollama y descargá un modelo con soporte de tools:

```bash
ollama pull qwen3.5:4b
export MODEL_PROVIDER=ollama
export OLLAMA_MODEL_ID=qwen3.5:4b
export OLLAMA_HOST=http://localhost:11434
```

Ollama evita depender de una cuenta cloud, pero la calidad del tool calling
depende del modelo y del hardware disponible. Bedrock será el camino principal
del workshop; Ollama es una alternativa útil y un buen punto de comparación.
Los ejemplos desactivan el modo de razonamiento de Ollama para mantener una
latencia razonable durante el workshop.

La alternativa local fue validada con `qwen3.5:4b` en una Mac con aceleración
Metal. Ejecutar modelos de este tamaño sólo con CPU funciona, pero puede ser
demasiado lento para una experiencia interactiva.

## Primeras pruebas

```bash
python 01-hello-agent/agent.py
python 02-schedule-data/schedule.py stats
python 03-schedule-tools/agent.py \
  "¿Qué charlas presenciales de infraestructura hay el viernes?"
```

## Agenda de Nerdearla

- Página: <https://nerdearla.com/argentina/schedule/>
- API: `https://backstage.nerdearla.com/api/sessions/?event_id=...`
- Zona horaria: `America/Argentina/Buenos_Aires`

El `event_id` cambia por edición. El importador lo recibe mediante
`NERDEARLA_EVENT_ID` y conserva un snapshot local como fallback. Las
descripciones y biografías son datos externos no confiables: el agente debe
tratarlas como contenido, nunca como instrucciones.

## Próximos checkpoints

Las siguientes etapas del workshop agregarán planificación personal sin
superposiciones, notas persistentes, observabilidad y un bonus multi-agent.
Se incorporarán al repositorio cuando tengan código y pruebas ejecutables.

## Referencias

- [Strands samples](https://github.com/strands-agents/samples)
- [Quickstart de Strands para Python](https://strandsagents.com/docs/user-guide/quickstart/python/)
- [Model providers](https://strandsagents.com/docs/user-guide/concepts/model-providers/)
- [Custom tools](https://strandsagents.com/docs/user-guide/concepts/tools/)

## Licencia

Este proyecto se distribuye bajo la [licencia Apache 2.0](LICENSE).
