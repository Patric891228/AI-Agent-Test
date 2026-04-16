import logging


class ConsoleOverlay:
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    def render(self, translated_text: str) -> None:
        self._logger.info("Overlay output: %s", translated_text)
