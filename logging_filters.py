# logging_filters.py
"""Filtros de logging para ocultar secretos en mensajes de log."""
from __future__ import annotations
import logging
import os
from typing import Final, Set

__all__ = ("RedactSecretsFilter",)

SENSITIVE_KEYS: Final[Set[str]] = {
    "SECRET_KEY",
    "FLASK_SECRET_KEY",
    "AWS_SECRET_ACCESS_KEY",
    "BREVO_API_KEY",
    "MAIL_PASSWORD",
    "GEMINI_API_KEY",
    "MONGO_URI",  # se trata aparte
}


class RedactSecretsFilter(logging.Filter):
    """
    Filtro de logging que redacciona secretos si aparecen por accidente.
    Nunca debe lanzar excepción.
    """

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        try:
            msg = str(record.getMessage())

            # Redactar MONGO_URI si apareciera literal
            mongo_uri = os.getenv("MONGO_URI")
            if mongo_uri and mongo_uri in msg:
                msg = msg.replace(mongo_uri, "***REDACT:URI***")

            # Redactar otras variables si su valor aparece en el mensaje
            for key in SENSITIVE_KEYS:
                val = os.getenv(key)
                if val and val in msg:
                    msg = msg.replace(val, "***REDACT***")

            record.msg = msg
        except Exception:
            # No bloquear logging por errores del filtro
            return True
        return True
