from __future__ import annotations

from typing import Any


def summarize_outcome(payload: dict[str, Any]) -> dict[str, Any]:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    analysis = data.get("analysis") if isinstance(data.get("analysis"), dict) else {}
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    return {
        "conversation_id": data.get("conversation_id"),
        "summary": analysis.get("transcript_summary"),
        "language": metadata.get("language"),
        "escalated": bool(metadata.get("escalated", False)),
    }
