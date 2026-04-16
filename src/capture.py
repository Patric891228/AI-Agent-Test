import sys
import time
from dataclasses import dataclass
from typing import Protocol

from src.config import AppConfig, ROI

SRCCOPY = 0x00CC0020
DIB_RGB_COLORS = 0
BI_RGB = 0


class CaptureBackend(Protocol):
    def capture_region(self, roi: ROI) -> bytes:
        ...


@dataclass(frozen=True)
class Frame:
    roi: tuple[int, int, int, int]
    content_id: str
    captured_at: float
    image_bytes: bytes
    image_format: str = "bgra"


class ScreenCapture:
    def __init__(self, config: AppConfig, capturer: CaptureBackend | None = None) -> None:
        self._config = config
        self._capturer = capturer or self._create_default_backend()

    def capture(self) -> Frame:
        roi = self._config.roi
        captured_at = time.perf_counter()
        return Frame(
            roi=(roi.x, roi.y, roi.w, roi.h),
            content_id=f"screen-{captured_at:.6f}",
            captured_at=captured_at,
            image_bytes=self._capturer.capture_region(roi),
        )

    @staticmethod
    def _create_default_backend() -> CaptureBackend:
        if sys.platform != "win32":
            raise RuntimeError("Real screen capture is currently supported on Windows only.")
        return Win32ScreenCapturer()


class Win32ScreenCapturer:
    def __init__(self) -> None:
        import ctypes
        from ctypes import wintypes

        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", wintypes.DWORD),
                ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG),
                ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD),
                ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG),
                ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD),
            ]

        class RGBQUAD(ctypes.Structure):
            _fields_ = [
                ("rgbBlue", ctypes.c_ubyte),
                ("rgbGreen", ctypes.c_ubyte),
                ("rgbRed", ctypes.c_ubyte),
                ("rgbReserved", ctypes.c_ubyte),
            ]

        class BITMAPINFO(ctypes.Structure):
            _fields_ = [
                ("bmiHeader", BITMAPINFOHEADER),
                ("bmiColors", RGBQUAD * 1),
            ]

        self._ctypes = ctypes
        self._wintypes = wintypes
        self._bitmap_info_cls = BITMAPINFO
        self._bitmap_info_header_cls = BITMAPINFOHEADER
        self._user32 = ctypes.WinDLL("user32", use_last_error=True)
        self._gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)

        self._user32.GetDC.argtypes = [wintypes.HWND]
        self._user32.GetDC.restype = wintypes.HDC
        self._user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
        self._user32.ReleaseDC.restype = ctypes.c_int

        self._gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
        self._gdi32.CreateCompatibleDC.restype = wintypes.HDC
        self._gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
        self._gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
        self._gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
        self._gdi32.SelectObject.restype = wintypes.HGDIOBJ
        self._gdi32.BitBlt.argtypes = [
            wintypes.HDC,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.HDC,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.DWORD,
        ]
        self._gdi32.BitBlt.restype = wintypes.BOOL
        self._gdi32.GetDIBits.argtypes = [
            wintypes.HDC,
            wintypes.HBITMAP,
            wintypes.UINT,
            wintypes.UINT,
            ctypes.c_void_p,
            ctypes.POINTER(BITMAPINFO),
            wintypes.UINT,
        ]
        self._gdi32.GetDIBits.restype = ctypes.c_int
        self._gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
        self._gdi32.DeleteObject.restype = wintypes.BOOL
        self._gdi32.DeleteDC.argtypes = [wintypes.HDC]
        self._gdi32.DeleteDC.restype = wintypes.BOOL

    def capture_region(self, roi: ROI) -> bytes:
        ctypes = self._ctypes

        if roi.w <= 0 or roi.h <= 0:
            raise ValueError("ROI width and height must be positive.")

        screen_dc = self._user32.GetDC(0)
        if not screen_dc:
            raise ctypes.WinError(ctypes.get_last_error())

        memory_dc = self._gdi32.CreateCompatibleDC(screen_dc)
        if not memory_dc:
            self._user32.ReleaseDC(0, screen_dc)
            raise ctypes.WinError(ctypes.get_last_error())

        bitmap = self._gdi32.CreateCompatibleBitmap(screen_dc, roi.w, roi.h)
        if not bitmap:
            self._gdi32.DeleteDC(memory_dc)
            self._user32.ReleaseDC(0, screen_dc)
            raise ctypes.WinError(ctypes.get_last_error())

        previous_bitmap = self._gdi32.SelectObject(memory_dc, bitmap)
        if not previous_bitmap:
            self._gdi32.DeleteObject(bitmap)
            self._gdi32.DeleteDC(memory_dc)
            self._user32.ReleaseDC(0, screen_dc)
            raise ctypes.WinError(ctypes.get_last_error())

        try:
            if not self._gdi32.BitBlt(
                memory_dc,
                0,
                0,
                roi.w,
                roi.h,
                screen_dc,
                roi.x,
                roi.y,
                SRCCOPY,
            ):
                raise ctypes.WinError(ctypes.get_last_error())

            stride = roi.w * 4
            image_size = stride * roi.h
            buffer = (ctypes.c_ubyte * image_size)()

            bitmap_info = self._bitmap_info_cls()
            bitmap_info.bmiHeader.biSize = ctypes.sizeof(self._bitmap_info_header_cls)
            bitmap_info.bmiHeader.biWidth = roi.w
            bitmap_info.bmiHeader.biHeight = -roi.h
            bitmap_info.bmiHeader.biPlanes = 1
            bitmap_info.bmiHeader.biBitCount = 32
            bitmap_info.bmiHeader.biCompression = BI_RGB
            bitmap_info.bmiHeader.biSizeImage = image_size

            lines_copied = self._gdi32.GetDIBits(
                memory_dc,
                bitmap,
                0,
                roi.h,
                buffer,
                ctypes.byref(bitmap_info),
                DIB_RGB_COLORS,
            )
            if lines_copied != roi.h:
                raise ctypes.WinError(ctypes.get_last_error())

            return bytes(buffer)
        finally:
            self._gdi32.SelectObject(memory_dc, previous_bitmap)
            self._gdi32.DeleteObject(bitmap)
            self._gdi32.DeleteDC(memory_dc)
            self._user32.ReleaseDC(0, screen_dc)
