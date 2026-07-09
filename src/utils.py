from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd
import yaml


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_params() -> Dict[str, Any]:
    with open(project_root() / "params.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_csv_semicolon(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=";")


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
