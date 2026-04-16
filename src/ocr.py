class StubOCR:
    def extract_text(self, image_bytes: bytes) -> str:
        return f"Detected text from image buffer ({len(image_bytes)} bytes)"
