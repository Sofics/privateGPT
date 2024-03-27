import logging
from typing import Any

from llama_index.llms.ollama import Ollama
from pydantic import Field

logger = logging.getLogger(__name__)


class CustomOllama(Ollama):
    """Custom llama_index Ollama class with the only intention of passing on the keep_alive parameter."""

    keep_alive: str = Field(
        default="5m",
        description="String that describes the time the model should stay in (V)RAM after last request.",
    )

    def __init__(self, *args, **kwargs) -> None:
        keep_alive = kwargs.pop('keep_alive', '5m')  # fetch keep_alive from kwargs or use 5m if not found.
        logger.warning("########## %s ##########", keep_alive)
        super().__init__(*args, **kwargs)
        self.keep_alive = keep_alive

    def _get_all_kwargs(self, **kwargs: Any) -> dict:
        post_req_remaining_dict = {
            **self._model_kwargs,
            **kwargs,
            "keep_alive": self.keep_alive
        }

        logger.warning("########## %s ##########", post_req_remaining_dict)

        return post_req_remaining_dict
