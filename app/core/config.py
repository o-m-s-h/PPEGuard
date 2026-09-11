import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    model_path: Path = Path(os.getenv("PPEGUARD_MODEL", str(ROOT / "models/best.pt")))
    output_dir: Path = Path(os.getenv("PPEGUARD_OUTPUTS", str(ROOT / "outputs/api")))
    max_upload_bytes: int = 100 * 1024 * 1024
