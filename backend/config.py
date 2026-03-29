"""Settings: QCAD path from env, backend/.env, or common Windows install paths."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent


def _env_path_qcad() -> str | None:
    """Read directly from the OS env (reliable even if Pydantic alias mapping fails)."""
    for key in ("NEXTKRAFT_QCAD", "QCAD_EXECUTABLE"):
        v = os.environ.get(key, "").strip().strip('"')
        if v:
            return v
    return None


def _find_qcad_windows() -> str | None:
    if sys.platform != "win32":
        return None
    roots = [
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
    ]
    for root in roots:
        base = Path(root)
        if not base.is_dir():
            continue
        try:
            for child in base.iterdir():
                if not child.is_dir():
                    continue
                name = child.name.lower()
                if "qcad" not in name:
                    continue
                exe = child / "qcad.exe"
                if exe.is_file():
                    return str(exe)
        except OSError:
            continue
    return None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    qcad_exe: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "NEXTKRAFT_QCAD",
            "QCAD_EXECUTABLE",
        ),
    )

    template_dxf: Path = _BACKEND_DIR / "templates" / "parking_template.dxf"
    temp_parent: Path | None = None

    def resolved_qcad_exe(self) -> str | None:
        """Prefer explicit field, then OS env, then auto-detect on Windows."""
        if self.qcad_exe:
            return self.qcad_exe.strip().strip('"')
        direct = _env_path_qcad()
        if direct:
            return direct
        return _find_qcad_windows()

    @property
    def qcad_path(self) -> Path | None:
        """Return QCAD exe path, or None if not configured (PDF rendering uses ezdxf now)."""
        raw = self.resolved_qcad_exe()
        if not raw:
            return None
        p = Path(raw)
        return p if p.is_file() else None


@lru_cache
def get_settings() -> Settings:
    return Settings()
