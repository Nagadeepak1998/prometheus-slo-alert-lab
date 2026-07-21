from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from prometheus_slo_alert_lab.models import AlertRoute, SloConfig


def load_config(path: str | Path) -> SloConfig:
    with Path(path).open("r", encoding="utf-8") as handle:
        data: dict[str, Any] = yaml.safe_load(handle) or {}
    return SloConfig.model_validate(data)


def load_metrics(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or []
    if not isinstance(data, list):
        raise ValueError("metrics file must contain a list of metric windows")
    return data


def load_scenario(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or []
    if not isinstance(data, list):
        raise ValueError("scenario file must contain a list of stages")
    return data


def load_history(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or []
    if not isinstance(data, list):
        raise ValueError("history file must contain a list of review windows")
    return data


def load_routes(path: str | Path) -> list[AlertRoute]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or []
    if not isinstance(data, list):
        raise ValueError("routes file must contain a list of alert routes")
    return [AlertRoute.model_validate(item) for item in data]
