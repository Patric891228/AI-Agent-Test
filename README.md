# PC Game Realtime Translator V1

This project is a minimal Python skeleton for a PC game realtime translation pipeline.

## Modules

- `capture`: captures a configured ROI every fixed interval
- `ocr`: OCR interface stub
- `translate`: translation interface stub
- `pipeline`: orchestrates capture, OCR, translation, logging, and timing
- `overlay`: overlay output stub
- `config`: loads YAML configuration

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python main.py
```

The app runs three pipeline iterations and prints logging output to the console.

## Config

Edit `config.yaml`:

```yaml
source_lang: ja
target_lang: zh-TW
capture_interval_ms: 300
roi:
  x: 100
  y: 100
  w: 640
  h: 180
```

## Test

```bash
python -m unittest discover -s tests -v
```

## Current V1 Behavior

- Capture uses a stub frame with ROI metadata
- OCR returns a fixed-style string
- Translation returns a fixed-style translated string
- Overlay logs the translated text instead of drawing on screen

## Next Extensions

- Replace `ScreenCapture` with actual desktop or window capture
- Replace `StubOCR` with Tesseract, PaddleOCR, or a cloud OCR provider
- Replace `StubTranslator` with a local or remote translation backend
- Add text deduplication and change detection to reduce redundant OCR calls
- Render translated text through a real transparent overlay window
- Add async execution and backpressure control for lower latency
