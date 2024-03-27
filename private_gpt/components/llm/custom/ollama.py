from typing import Any

from llama_index.llms.ollama import Ollama
from pydantic import Field


class CustomOllama(Ollama):
    """Custom llama_index Ollama class with the only intention of passing on the keep_alive parameter."""

    keep_alive: str = Field(
        default="5m",
        description="String that describes the time the model should stay in (V)RAM after last request.",
    )

    def __init__(self, *args, keep_alive: str = "5m", **kwargs) -> None:
        self.keep_alive = keep_alive
        super().__init__(*args, **kwargs)

    def stream_complete(self, prompt: str, **kwargs: Any):
        return super().stream_complete(self, prompt, keep_alive=self.keep_alive, **kwargs)
