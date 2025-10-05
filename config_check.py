# config_check.py
"""Validación de variables críticas en tiempo de arranque."""
from __future__ import annotations
import os
from typing import Final, List

__all__ = ("validate_required",)

REQUIRED_IN_PROD: Final = ("SECRET_KEY", "MONGO_URI")


def validate_required() -> None:
    """
    Lanza RuntimeError en producción si faltan variables críticas.
    No imprime valores por seguridad.
    """
    env = os.getenv("FLASK_ENV", "production").lower()
    if env == "production":
        missing: List[str] = [k for k in REQUIRED_IN_PROD if not os.getenv(k)]
        if missing:
            raise RuntimeError(
                "Variables obligatorias ausentes en producción: "
                + ", ".join(missing)
                + ". Defínelas en .env o variables de entorno. (Valores no mostrados por seguridad)"
            )
