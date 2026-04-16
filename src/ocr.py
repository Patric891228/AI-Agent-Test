from src.capture import Frame


class StubOCR:
    def extract_text(self, frame: Frame) -> str:
        return f"Detected text from {frame.content_id}"
