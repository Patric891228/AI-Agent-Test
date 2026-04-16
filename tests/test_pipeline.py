import unittest

from src.capture import Frame
from src.config import AppConfig, ROI
from src.pipeline import TranslationPipeline


class FakeCapture:
    def capture(self) -> Frame:
        return Frame(roi=(0, 0, 100, 50), content_id="test-frame", captured_at=0.0)


class FakeOCR:
    def extract_text(self, frame: Frame) -> str:
        return f"text:{frame.content_id}"


class FakeTranslator:
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        return f"{source_lang}->{target_lang}:{text}"


class FakeOverlay:
    def __init__(self) -> None:
        self.messages = []

    def render(self, translated_text: str) -> None:
        self.messages.append(translated_text)


class TranslationPipelineTest(unittest.TestCase):
    def test_pipeline_runs_end_to_end(self) -> None:
        overlay = FakeOverlay()
        config = AppConfig(
            source_lang="ja",
            target_lang="zh-TW",
            capture_interval_ms=0,
            roi=ROI(x=0, y=0, w=100, h=50),
        )
        pipeline = TranslationPipeline(
            capture=FakeCapture(),
            ocr=FakeOCR(),
            translator=FakeTranslator(),
            config=config,
            interval_ms=0,
            overlay=overlay,
        )

        result = pipeline.run_once()

        self.assertEqual(result.source_text, "text:test-frame")
        self.assertEqual(result.translated_text, "ja->zh-TW:text:test-frame")
        self.assertGreaterEqual(result.elapsed_ms, 0)
        self.assertEqual(overlay.messages, ["ja->zh-TW:text:test-frame"])


if __name__ == "__main__":
    unittest.main()
