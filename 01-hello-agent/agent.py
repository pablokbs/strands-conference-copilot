"""Primer agente del workshop: una invocación, todavía sin tools."""

from __future__ import annotations

import os

from strands import Agent
from strands.models import BedrockModel
from strands.models.ollama import OllamaModel


def create_model() -> BedrockModel | OllamaModel:
    """Create the model selected through MODEL_PROVIDER."""
    provider = os.getenv("MODEL_PROVIDER", "bedrock").lower()

    if provider == "bedrock":
        return BedrockModel(
            model_id=os.getenv(
                "BEDROCK_MODEL_ID",
                "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            ),
            region_name=os.getenv("AWS_REGION", "us-west-2"),
            temperature=0.2,
        )

    if provider == "ollama":
        return OllamaModel(
            model_id=os.getenv("OLLAMA_MODEL_ID", "qwen3:4b"),
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            additional_args={"think": False},
            temperature=0.2,
            max_tokens=2048,
            options={"num_ctx": 8192},
        )

    raise ValueError("MODEL_PROVIDER must be 'bedrock' or 'ollama'")


def main() -> None:
    agent = Agent(
        model=create_model(),
        callback_handler=None,
        system_prompt=(
            "Sos el Conference Copilot de Nerdearla. "
            "Respondé en español, de forma breve y útil."
        ),
    )
    response = agent(
        "Hola. Presentate en dos oraciones y contame qué vamos a construir."
    )
    print(response)


if __name__ == "__main__":
    main()
