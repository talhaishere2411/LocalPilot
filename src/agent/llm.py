"""Client for an OpenAI-compatible local model server (Ollama, mlx-lm).

Owner: Developer B (task B1).
"""

from collections.abc import Iterator

DEFAULT_MODEL = "gemma3:4b-instruct"
DEFAULT_BASE_URL = "http://localhost:11434/v1"


class LLMClient:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
    ) -> None:
        raise NotImplementedError

    def get_completion(
        self,
        messages: list[dict],
        temperature: float = 0.2,
        model: str | None = None,
    ) -> Iterator[str]:
        """Stream the model's reply as text chunks.

        `model` overrides the client's default model for this call.
        """
        raise NotImplementedError
