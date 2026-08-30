# 01 — Hello Agent

Objetivo: crear el agente Strands más pequeño posible y comprobar que puede
hablar con el model provider elegido.

```bash
python agent.py
```

El script usa Bedrock por defecto. Definí `MODEL_PROVIDER=ollama` para usar el
servidor Ollama configurado en `OLLAMA_HOST`.

Conceptos:

- `Agent`;
- system prompt;
- model provider;
- invocación del agent loop.
