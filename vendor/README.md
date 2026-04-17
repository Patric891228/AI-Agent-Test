Place a portable Tesseract distribution under `vendor/tesseract/`.

Expected layout:

```text
vendor/
  tesseract/
    tesseract.exe
    tessdata/
      jpn.traineddata
      chi_tra.traineddata
```

When present, the app will prefer this bundled Tesseract binary over a system-wide installation.
