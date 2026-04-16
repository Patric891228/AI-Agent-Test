from dataclasses import dataclass

try:
    import yaml
except ModuleNotFoundError:
    yaml = None


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
        raw = _safe_load_yaml(file.read())

    roi = raw["roi"]
    return AppConfig(
        source_lang=raw["source_lang"],
        target_lang=raw["target_lang"],
        capture_interval_ms=raw["capture_interval_ms"],
        roi=ROI(x=roi["x"], y=roi["y"], w=roi["w"], h=roi["h"]),
    )


def _safe_load_yaml(text: str) -> dict:
    if yaml is not None:
        return yaml.safe_load(text)
    return _load_simple_yaml(text)


def _load_simple_yaml(text: str) -> dict:
    root: dict[str, object] = {}
    current_section: dict[str, object] | None = None

    for raw_line in text.splitlines():
        if not raw_line.strip():
            continue

        if raw_line.startswith("  "):
            if current_section is None:
                raise ValueError("Invalid config structure: nested field without a section.")
            key, value = raw_line.strip().split(":", maxsplit=1)
            current_section[key.strip()] = _parse_scalar(value.strip())
            continue

        key, value = raw_line.split(":", maxsplit=1)
        key = key.strip()
        value = value.strip()

        if value:
            root[key] = _parse_scalar(value)
            current_section = None
            continue

        current_section = {}
        root[key] = current_section

    return root


def _parse_scalar(value: str) -> int | str:
    try:
        return int(value)
    except ValueError:
        return value
