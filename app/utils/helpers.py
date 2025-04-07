from datetime import datetime, timezone
from typing import Any


def extract_jti(payload: dict) -> str | None:
    jti = payload.get("jti")
    return jti


def handle_failed_message(msg: Any, error: str):
    payload = {
        "original_message": msg,
        "error": error,
        "timestamp": datetime.now(tz=timezone.utc),
    }
    return payload
