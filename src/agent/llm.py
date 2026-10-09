"""Client for an OpenAI-compatible local model server (Ollama, mlx-lm).

Owner: Developer B (task B1).
"""

import json
from collections.abc import Iterator

import httpx

DEFAULT_MODEL = "qwen2.5-coder:7b"
DEFAULT_BASE_URL = "http://localhost:11434/v1"


class LLMClient:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 120.0,
    ) -> None:
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

    def get_completion(
        self,
        messages: list[dict],
        temperature: float = 0.2,
        model: str | None = None,
    ) -> Iterator[str]:
        """Stream the model's reply as text chunks.

        `model` overrides the client's default model for this call.
        """
        use_model = model if model is not None else self.model
        
        payload = {
            "model": use_model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        
        with httpx.Client(timeout=self.timeout) as client:
            with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
            ) as response:
                response.raise_for_status()
                
                for line in response.iter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Skip "data: " prefix
                    if line.startswith("data: "):
                        line = line[6:]
                    
                    # Skip [DONE] marker
                    if line == "[DONE]":
                        break
                    
                    # Parse JSON chunk
                    try:
                        chunk = json.loads(line)
                        
                        # Extract content from delta
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        # Skip malformed JSON
                        continue
