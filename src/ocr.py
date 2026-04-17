import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

from src.capture import Frame

TESSERACT_LANGUAGE_MAP = {
    "en": "eng",
    "ja": "jpn",
    "zh-CN": "chi_sim",
    "zh-TW": "chi_tra",
}


class TesseractOCR:
    def __init__(
        self,
        source_lang: str,
        command: str | None = None,
        runner=None,
    ) -> None:
        self._source_lang = TESSERACT_LANGUAGE_MAP.get(source_lang, source_lang)
        self._command = command or _resolve_tesseract_command()
        self._extra_env = _build_tesseract_env(self._command)
        self._runner = runner or subprocess.run

    def extract_text(self, frame: Frame) -> str:
        if self._runner is subprocess.run and not _command_exists(self._command):
            raise RuntimeError(
                f"Tesseract executable '{self._command}' was not found. "
                "Bundle Tesseract with the app or install it and make sure it is available on PATH."
            )

        image = _frame_to_image(frame)
        temp_path = _write_temp_image(image)
        try:
            completed = self._runner(
                [
                    self._command,
                    str(temp_path),
                    "stdout",
                    "-l",
                    self._source_lang,
                    "--psm",
                    "6",
                ],
                capture_output=True,
                text=True,
                check=False,
                env=self._extra_env,
            )
        finally:
            temp_path.unlink(missing_ok=True)

        if completed.returncode != 0:
            error_text = completed.stderr.strip() or "Unknown Tesseract error."
            raise RuntimeError(f"Tesseract OCR failed: {error_text}")

        return completed.stdout.strip()


def _frame_to_image(frame: Frame) -> Image.Image:
    width = frame.roi[2]
    height = frame.roi[3]
    expected_size = width * height * 4

    if frame.image_format != "bgra":
        raise ValueError(f"Unsupported frame image format: {frame.image_format}")
    if len(frame.image_bytes) != expected_size:
        raise ValueError(
            "BGRA frame size does not match ROI dimensions: "
            f"expected {expected_size} bytes, got {len(frame.image_bytes)}."
        )

    return Image.frombytes("RGBA", (width, height), frame.image_bytes, "raw", "BGRA")


def _write_temp_image(image: Image.Image) -> Path:
    file_descriptor, temp_name = tempfile.mkstemp(suffix=".png")
    try:
        os.close(file_descriptor)
        image.save(temp_name, format="PNG")
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise

    return Path(temp_name)


def _resolve_tesseract_command() -> str:
    env_override = os.environ.get("AI_AGENT_TESSERACT_CMD")
    if env_override:
        return env_override

    for base_dir in _runtime_search_roots():
        for candidate in (
            base_dir / "tesseract" / "tesseract.exe",
            base_dir / "vendor" / "tesseract" / "tesseract.exe",
            base_dir / "tesseract.exe",
        ):
            if candidate.exists():
                return str(candidate)

    return "tesseract"


def _build_tesseract_env(command: str) -> dict[str, str]:
    env = os.environ.copy()
    tessdata_dir = _find_tessdata_dir(command)
    if tessdata_dir is not None:
        env["TESSDATA_PREFIX"] = str(tessdata_dir)
    return env


def _find_tessdata_dir(command: str) -> Path | None:
    command_path = Path(command)
    if command_path.exists():
        for candidate in (
            command_path.parent / "tessdata",
            command_path.parent.parent / "tessdata",
        ):
            if candidate.exists():
                return candidate

    for base_dir in _runtime_search_roots():
        for candidate in (
            base_dir / "tessdata",
            base_dir / "tesseract" / "tessdata",
            base_dir / "vendor" / "tesseract" / "tessdata",
        ):
            if candidate.exists():
                return candidate

    return None


def _runtime_search_roots() -> list[Path]:
    roots = [Path.cwd(), Path(__file__).resolve().parents[1]]

    if getattr(sys, "frozen", False):
        roots.append(Path(sys.executable).resolve().parent)

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        roots.append(Path(meipass))

    unique_roots: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        resolved = root.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_roots.append(resolved)
    return unique_roots


def _command_exists(command: str) -> bool:
    command_path = Path(command)
    if command_path.exists():
        return True
    return shutil.which(command) is not None
