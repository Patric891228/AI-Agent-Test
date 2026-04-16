from dataclasses import dataclass

import yaml


@dataclass(frozen=True)
class ROI:
    x: int
    y: int
    w: int
    h: int


@dataclass(frozen=True)
class AppConfig:
    source_lang: str
    target_lang: str
    capture_interval_ms: int
    roi: ROI


def load_config(path: str) -> AppConfig:
    with open(path, "r", encoding="utf-8") as file:
        raw = yaml.safe_load(file)

    roi = raw["roi"]
    return AppConfig(
        source_lang=raw["source_lang"],
        target_lang=raw["target_lang"],
        capture_interval_ms=raw["capture_interval_ms"],
        roi=ROI(x=roi["x"], y=roi["y"], w=roi["w"], h=roi["h"]),
    )
