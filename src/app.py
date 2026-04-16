import logging

from src.capture import ScreenCapture
from src.config import load_config
from src.ocr import StubOCR
from src.pipeline import TranslationPipeline
from src.translate import StubTranslator


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def run() -> None:
    configure_logging()
    config = load_config("config.yaml")
    pipeline = TranslationPipeline(
        capture=ScreenCapture(config),
        ocr=StubOCR(),
        translator=StubTranslator(),
        config=config,
        interval_ms=config.capture_interval_ms,
    )
    pipeline.run(iterations=3)
