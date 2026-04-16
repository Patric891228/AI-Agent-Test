import tempfile
import unittest
from pathlib import Path

from src.capture import ScreenCapture
from src.config import AppConfig, ROI, load_config


class FakeCaptureBackend:
    def __init__(self) -> None:
        self.calls = []

    def capture_region(self, roi: ROI) -> bytes:
        self.calls.append(roi)
        return b"pixel-bytes"


class ConfigAndCaptureTest(unittest.TestCase):
    def test_load_config_parses_roi(self) -> None:
        config_text = """
source_lang: en
target_lang: zh-TW
capture_interval_ms: 150
roi:
  x: 5
  y: 10
  w: 320
  h: 120
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.yaml"
            config_path.write_text(config_text, encoding="utf-8")

            config = load_config(str(config_path))

        self.assertEqual(config.source_lang, "en")
        self.assertEqual(config.target_lang, "zh-TW")
        self.assertEqual(config.capture_interval_ms, 150)
        self.assertEqual(config.roi, ROI(x=5, y=10, w=320, h=120))

    def test_screen_capture_returns_real_image_payload_from_backend(self) -> None:
        backend = FakeCaptureBackend()
        config = AppConfig(
            source_lang="ja",
            target_lang="zh-TW",
            capture_interval_ms=300,
            roi=ROI(x=11, y=22, w=33, h=44),
        )

        frame = ScreenCapture(config, capturer=backend).capture()

        self.assertEqual(frame.roi, (11, 22, 33, 44))
        self.assertEqual(frame.image_bytes, b"pixel-bytes")
        self.assertEqual(frame.image_format, "bgra")
        self.assertEqual(len(backend.calls), 1)
        self.assertEqual(backend.calls[0], config.roi)
        self.assertTrue(frame.content_id.startswith("screen-"))


if __name__ == "__main__":
    unittest.main()
