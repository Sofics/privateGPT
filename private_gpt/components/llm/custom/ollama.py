"""Custom llama_index ollama class with the only intention of passing on the keep_alive parameter"""

from typing import Any, Optional, Dict, Callable

from llama_index.callbacks import CallbackManager
from llama_index.constants import DEFAULT_CONTEXT_WINDOW
from llama_index.llms import CompletionResponseGen
from llama_index.llms.ollama import Ollama


class CustomOllama(Ollama):
    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        temperature: float = 0.75,
        additional_kwargs: Optional[Dict[str, Any]] = None,
        context_window: int = DEFAULT_CONTEXT_WINDOW,
        prompt_key: str = "prompt",
        messages_to_prompt: Optional[Callable] = None,
        completion_to_prompt: Optional[Callable] = None,
        callback_manager: Optional[CallbackManager] = None,
        keep_alive: str = "5m",
    ) -> None:
        self.keep_alive = keep_alive
        super().__init__(
            model,
            base_url,
            temperature,
            additional_kwargs,
            context_window,
            prompt_key,
            messages_to_prompt,
            completion_to_prompt,
            callback_manager
        )

    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        return super().stream_complete(self, prompt, keep_alive=self.keep_alive, **kwargs)
