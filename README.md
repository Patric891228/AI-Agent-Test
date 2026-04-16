# PC Game Realtime Translator V1

This project is a minimal runnable skeleton for a PC game realtime translation pipeline.

The current goal is not full translation quality yet. The goal is to keep the project executable end to end, with clear module boundaries so the stub implementations can be replaced incrementally.

## Current Status

The project currently works as a V1 skeleton.

Implemented:

- Config loading from `config.yaml`
- Periodic pipeline execution every `capture_interval_ms`
- Real ROI screenshot capture on Windows
- ROI metadata flow through the capture stage
- OCR stub
- Translation stub
- Console logging for pipeline result and elapsed time
- Unit tests for pipeline wiring, config parsing, and capture behavior

Not implemented yet:

- Real OCR engine
- Real translation backend
- Real on-screen overlay
- Duplicate text filtering
- Async pipeline scheduling

## Project Structure

- `main.py`: application entry point
- `config.yaml`: runtime config
- `src/app.py`: bootstraps config, logging, and pipeline
- `src/config.py`: YAML loader and config dataclasses
- `src/capture.py`: ROI screen capture and frame image payload generation
- `src/ocr.py`: OCR stub
- `src/translate.py`: translation stub
- `src/pipeline.py`: capture -> OCR -> translate -> overlay orchestration
- `src/overlay.py`: console overlay stub
- `tests/test_pipeline.py`: minimal end-to-end unit test for pipeline wiring
- `tests/test_config.py`: config parsing and capture behavior tests

## How To Run Locally

Recommended setup:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run the app:

```bash
python main.py
```

Current runtime behavior:

- Runs the pipeline 3 times
- Waits about `300ms` between iterations
- Logs translated output and total elapsed time to console

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Config

Current config file:

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

Fields:

- `source_lang`: OCR source language
- `target_lang`: translation target language
- `capture_interval_ms`: pipeline interval in milliseconds
- `roi`: region of interest for desktop ROI capture

## Current V1 Behavior

`ScreenCapture.capture()` currently returns a `Frame` with ROI metadata and raw BGRA screenshot bytes captured from the configured desktop region.

`StubOCR.extract_text()` currently returns:

```text
Detected text from image buffer (<n> bytes)
```

`StubTranslator.translate()` currently returns:

```text
[ja->zh-TW] translated: Detected text from image buffer (<n> bytes)
```

The overlay stage does not draw on screen yet. It only logs the translated text through the console.

## Known Constraints

- Real capture currently targets the desktop ROI only
- No game window binding yet
- No OCR accuracy or translation quality validation yet
- No CLI arguments yet
- `main.py` currently runs a fixed iteration count for demo purposes

## Suggested Next Step

The most reasonable next step is to replace the OCR stub with a real OCR backend now that capture returns real image data.

Recommended order:

1. Replace `StubOCR` with a real OCR backend
2. Decode the raw BGRA buffer into the image format expected by the OCR engine
3. Keep translation stubbed until OCR is stable
4. Add tests around OCR extraction behavior
5. Validate OCR quality against a few representative game screenshots

After that:

1. Add text deduplication to avoid repeated translation calls
2. Replace `StubTranslator` with a real translation service
3. Add a real transparent overlay window

## Resume Checklist

When resuming work on another device or in a new conversation, start with:

1. Open this repository
2. Create or activate the virtual environment
3. Run `pip install -r requirements.txt`
4. Run `python main.py`
5. Run `python -m unittest discover -s tests -v`
6. Continue from the "Suggested Next Step" section above

## Context For Future Work

This repository has already been initialized as a Git repo and pushed to GitHub.

If continuing development, keep the module boundaries stable:

- `capture` should only handle frame acquisition
- `ocr` should only convert image input into text
- `translate` should only translate text
- `pipeline` should orchestrate timing and data flow
- `overlay` should only render output

That separation will make it easier to swap implementations without rewriting the full app.
