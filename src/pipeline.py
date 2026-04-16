import logging
import time
from dataclasses import dataclass

from src.config import AppConfig
from src.overlay import ConsoleOverlay


@dataclass(frozen=True)
class PipelineResult:
    source_text: str
    translated_text: str
    elapsed_ms: float


class TranslationPipeline:
    def __init__(self, capture, ocr, translator, config: AppConfig, interval_ms: int, overlay=None) -> None:
        self._capture = capture
        self._ocr = ocr
        self._translator = translator
        self._config = config
        self._interval_ms = interval_ms
        self._overlay = overlay or ConsoleOverlay()
        self._logger = logging.getLogger(__name__)

    def run_once(self) -> PipelineResult:
        start = time.perf_counter()
        frame = self._capture.capture()
        source_text = self._ocr.extract_text(frame.image_bytes)
        translated_text = self._translator.translate(
            source_text,
            self._config.source_lang,
            self._config.target_lang,
        )
        self._overlay.render(translated_text)
        elapsed_ms = (time.perf_counter() - start) * 1000
        self._logger.info(
            "Pipeline result | roi=%s | source=%s | translated=%s | elapsed_ms=%.2f",
            frame.roi,
            source_text,
            translated_text,
            elapsed_ms,
        )
        return PipelineResult(
            source_text=source_text,
            translated_text=translated_text,
            elapsed_ms=elapsed_ms,
        )

    def run(self, iterations: int = 1) -> list[PipelineResult]:
        results = []
        for index in range(iterations):
            results.append(self.run_once())
            if index < iterations - 1:
                time.sleep(self._interval_ms / 1000)
        return results
