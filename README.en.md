# Nerdearla Conference Copilot with Strands

[Versión en español](README.md)

A progressive tutorial for learning the
[Strands Agents SDK](https://strandsagents.com/) by building an agent that
helps attendees navigate the Nerdearla Argentina 2026 schedule.

Participants can download the project before the workshop, connect a model,
and run each checkpoint without copying large blocks of code during the talk.

## What we are building

The final copilot will be able to:

- search sessions by topic, track, date, and time;
- recommend a personal schedule without conflicts;
- remember interests and selected sessions;
- save notes during talks;
- summarize what the attendee learned at the end of the day.

The schedule comes from the public API used by Nerdearla. The repository also
includes a local snapshot, so the workshop can continue even when conference
Wi-Fi decides to become a distributed resilience exercise.

## Checkpoints

| Stage | Concept | Status |
| --- | --- | --- |
| [`01-hello-agent`](01-hello-agent/) | First agent and model provider | Runnable |
| [`02-schedule-data`](02-schedule-data/) | External data and normalization | Runnable |
| [`03-schedule-tools`](03-schedule-tools/) | Custom tools and the agent loop | Runnable |

Each directory is a checkpoint that builds on the previous stages. You can
start from scratch or jump to a later stage if workshop time runs short, as
long as you download the complete repository.

## Requirements

- Python 3.10 or newer.
- An AWS account with access to Amazon Bedrock, **or** a local Ollama server.
- Git.

## Installation

```bash
git clone https://github.com/pablokbs/strands-conference-copilot.git
cd strands-conference-copilot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Option A: Amazon Bedrock

Configure AWS credentials using the standard AWS CLI workflow:

```bash
aws configure
aws sts get-caller-identity
```

Then select a region and model. The model must be enabled in your Bedrock
account.

```bash
export MODEL_PROVIDER=bedrock
export AWS_REGION=us-west-2
export BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
```

Never commit access keys to this repository or store them in tracked `.env`
files.

## Option B: Ollama

Install Ollama and download a model with tool-calling support:

```bash
ollama pull qwen3.5:4b
export MODEL_PROVIDER=ollama
export OLLAMA_MODEL_ID=qwen3.5:4b
export OLLAMA_HOST=http://localhost:11434
```

Ollama avoids requiring a cloud account, but tool-calling quality and latency
depend on the model and available hardware. Bedrock is the primary workshop
path; Ollama is a useful local alternative and comparison point. The examples
disable Ollama thinking mode to keep latency reasonable during the workshop.

The local path was validated with `qwen3.5:4b` on a Mac using Metal
acceleration. CPU-only inference works, but can be too slow for an interactive
workshop experience.

## First runs

```bash
python 01-hello-agent/agent.py
python 02-schedule-data/schedule.py stats
python 03-schedule-tools/agent.py \
  "Recommend three in-person security talks"
```

## Nerdearla schedule

- Page: <https://nerdearla.com/argentina/schedule/>
- API: `https://backstage.nerdearla.com/api/sessions/?event_id=...`
- Time zone: `America/Argentina/Buenos_Aires`

The `event_id` changes for each edition. The importer accepts it through
`NERDEARLA_EVENT_ID` and keeps a local snapshot as an offline fallback.
Descriptions and speaker biographies are untrusted external data: the agent
must treat them as content, never as instructions.

## Next checkpoints

Future workshop stages will add conflict-free personal planning, persistent
notes, observability, and a multi-agent bonus. They will be added once their
code and tests are runnable.

## References

- [Strands samples](https://github.com/strands-agents/samples)
- [Strands Python quickstart](https://strandsagents.com/docs/user-guide/quickstart/python/)
- [Model providers](https://strandsagents.com/docs/user-guide/concepts/model-providers/)
- [Custom tools](https://strandsagents.com/docs/user-guide/concepts/tools/)

## License

This project is distributed under the [Apache License 2.0](LICENSE).
