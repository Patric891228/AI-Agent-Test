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
- Real OCR backend wiring via Tesseract
- Translation stub
- Console logging for pipeline result and elapsed time
- Unit tests for pipeline wiring, config parsing, capture behavior, and OCR conversion

Not implemented yet:

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
- `src/ocr.py`: Tesseract OCR backend with BGRA frame decoding
- `src/translate.py`: translation stub
- `src/pipeline.py`: capture -> OCR -> translate -> overlay orchestration
- `src/overlay.py`: console overlay stub
- `tests/test_pipeline.py`: minimal end-to-end unit test for pipeline wiring
- `tests/test_config.py`: config parsing and capture behavior tests
- `tests/test_ocr.py`: OCR frame decoding and backend invocation tests

## How To Run Locally

Recommended setup:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Additional runtime dependency:

- Install Tesseract OCR and ensure `tesseract` is available on `PATH`
- Or place a portable copy under `vendor/tesseract/` so the app can use the bundled binary

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

`TesseractOCR.extract_text()` currently:

- Decodes the raw BGRA frame into a PNG image
- Prefers a bundled `vendor/tesseract/tesseract.exe` when present, otherwise falls back to the local `tesseract` on `PATH`
- Sets `TESSDATA_PREFIX` automatically when a nearby `tessdata` folder is found
- Invokes the resolved `tesseract` executable with the configured source language
- Returns the extracted OCR text after trimming trailing whitespace

`StubTranslator.translate()` currently returns:

```text
[ja->zh-TW] translated: Detected text from image buffer (<n> bytes)
```

The overlay stage does not draw on screen yet. It only logs the translated text through the console.

## Known Constraints

- Real capture currently targets the desktop ROI only
- OCR depends on Tesseract language packs, either from a local installation or a bundled `vendor/tesseract/tessdata`
- No game window binding yet
- No OCR quality or translation quality validation yet
- No CLI arguments yet
- `main.py` currently runs a fixed iteration count for demo purposes

## Packaging For Other Users

If you want to distribute the app without asking users to install Tesseract separately:

1. Put a portable Tesseract build in `vendor/tesseract/`
2. Make sure `vendor/tesseract/tessdata/` includes the languages your config needs, such as `jpn.traineddata` and `chi_tra.traineddata`
3. Install PyInstaller in the same Python environment you will use for packaging
4. Verify which Python executable your terminal is using:

```bash
where python
python -m PyInstaller --version
```

On Windows it is common to have multiple Python installations. If `python -m PyInstaller --version` works in your terminal, use that same terminal for packaging.

5. Build with either of these commands:

```bash
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
python -m PyInstaller --noconfirm AI-Agent-Test.spec
```

The PowerShell build script prefers `.venv\Scripts\python.exe` when that virtual environment exists and is healthy. If your terminal uses another Python installation, the direct `python -m PyInstaller --noconfirm AI-Agent-Test.spec` command is the safest option.

6. Distribute the generated executable from `dist/AI-Agent-Test.exe`

The included `AI-Agent-Test.spec` file automatically packages:

- `config.yaml`
- The whole `vendor/tesseract/` folder when it exists

If you need to override the OCR executable path manually, set:

```bash
AI_AGENT_TESSERACT_CMD=C:\path\to\tesseract.exe
```

Before sending the packaged app to someone else, do a local smoke test:

```bash
.\dist\AI-Agent-Test.exe
```

If the executable starts but OCR fails, check these first:

- `vendor/tesseract/tesseract.exe` exists
- `vendor/tesseract/tessdata/` exists
- The required language packs are present, for example `jpn.traineddata`
- `config.yaml` matches the language packs you bundled

## Suggested Next Step

The most reasonable next step is to reduce unnecessary translation work now that OCR is producing real text.

Recommended order:

1. Add duplicate text filtering so unchanged subtitles do not trigger repeated translations
2. Keep translation stubbed until OCR output is validated on representative screenshots
3. Add OCR-focused regression samples for a few common subtitle layouts
4. Replace `StubTranslator` with a real translation service
5. Add error handling and retries around OCR and translation failures

After that:

1. Add a real transparent overlay window
2. Add async pipeline scheduling
3. Add game-window binding instead of desktop-only ROI capture

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
