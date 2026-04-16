import time
from dataclasses import dataclass

from src.config import AppConfig


@dataclass(frozen=True)
class Frame:
    roi: tuple[int, int, int, int]
    content_id: str
    captured_at: float


class ScreenCapture:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def capture(self) -> Frame:
        roi = self._config.roi
        return Frame(
            roi=(roi.x, roi.y, roi.w, roi.h),
            content_id="stub-frame",
            captured_at=time.perf_counter(),
        )
