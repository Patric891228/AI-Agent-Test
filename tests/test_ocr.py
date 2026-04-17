import unittest
from pathlib import Path
from unittest.mock import patch

from src.capture import Frame
from src.ocr import TesseractOCR, _find_tessdata_dir, _frame_to_image, _resolve_tesseract_command


class FakeCompletedProcess:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class TesseractOCRTest(unittest.TestCase):
    def test_extract_text_converts_bgra_frame_and_calls_tesseract(self) -> None:
        calls = []

        def fake_runner(args, capture_output, text, check, env):
            calls.append(
                {
                    "args": args,
                    "capture_output": capture_output,
                    "text": text,
                    "check": check,
                    "env": env,
                }
            )
            self.assertTrue(Path(args[1]).exists())
            return FakeCompletedProcess(returncode=0, stdout="hello world\n")

        frame = Frame(
            roi=(0, 0, 1, 1),
            content_id="frame-1",
            captured_at=0.0,
            image_bytes=bytes([0, 0, 255, 255]),
        )

        text_result = TesseractOCR(source_lang="ja", runner=fake_runner).extract_text(frame)

        self.assertEqual(text_result, "hello world")
        self.assertEqual(len(calls), 1)
        self.assertTrue(calls[0]["args"][0].endswith("tesseract.exe") or calls[0]["args"][0] == "tesseract")
        self.assertEqual(calls[0]["args"][2:], ["stdout", "-l", "jpn", "--psm", "6"])
        self.assertTrue(calls[0]["capture_output"])
        self.assertTrue(calls[0]["text"])
        self.assertFalse(calls[0]["check"])
        self.assertIsInstance(calls[0]["env"], dict)

    def test_frame_to_image_rejects_invalid_bgra_size(self) -> None:
        frame = Frame(
            roi=(0, 0, 2, 2),
            content_id="frame-2",
            captured_at=0.0,
            image_bytes=b"too-short",
        )

        with self.assertRaisesRegex(ValueError, "expected 16 bytes"):
            _frame_to_image(frame)

    def test_resolve_tesseract_command_prefers_bundled_binary(self) -> None:
        bundled = Path("C:/bundle/tesseract/tesseract.exe")

        with patch("src.ocr._runtime_search_roots", return_value=[Path("C:/bundle")]):
            with patch.object(Path, "exists", autospec=True) as mock_exists:
                mock_exists.side_effect = lambda path_obj: path_obj == bundled
                command = _resolve_tesseract_command()

        self.assertEqual(command, str(bundled))

    def test_find_tessdata_dir_uses_directory_next_to_bundled_binary(self) -> None:
        command = "C:/bundle/tesseract/tesseract.exe"
        tessdata = Path("C:/bundle/tesseract/tessdata")

        with patch.object(Path, "exists", autospec=True) as mock_exists:
            mock_exists.side_effect = lambda path_obj: path_obj == Path(command) or path_obj == tessdata
            result = _find_tessdata_dir(command)

        self.assertEqual(result, tessdata)


if __name__ == "__main__":
    unittest.main()
