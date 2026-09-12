from __future__ import annotations

import hashlib
import hmac
import time


class WebhookSignatureError(ValueError):
    pass


def verify_elevenlabs_signature(
    raw_body: bytes,
    signature_header: str | None,
    secret: str,
    tolerance_seconds: int = 300,
    now: int | None = None,
) -> None:
    if not signature_header:
        raise WebhookSignatureError("missing signature")
    parts: dict[str, str] = {}
    for item in signature_header.split(","):
        key, sep, value = item.strip().partition("=")
        if sep:
            parts[key] = value
    if "t" not in parts or "v0" not in parts:
        raise WebhookSignatureError("malformed signature")
    try:
        timestamp = int(parts["t"])
    except ValueError as exc:
        raise WebhookSignatureError("invalid timestamp") from exc
    current = int(time.time()) if now is None else now
    if abs(current - timestamp) > tolerance_seconds:
        raise WebhookSignatureError("stale signature")
    signed_payload = f"{timestamp}.".encode() + raw_body
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, parts["v0"]):
        raise WebhookSignatureError("invalid signature")
