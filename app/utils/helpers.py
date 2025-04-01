def extract_jti(payload: dict) -> str | None:
    jti = payload.get("jti")
    return jti
