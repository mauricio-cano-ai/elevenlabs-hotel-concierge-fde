from __future__ import annotations

from typing import Any, cast


def summarize_outcome(payload: dict[str, Any]) -> dict[str, Any]:
    raw_data = payload.get("data")
    data = cast(dict[str, Any], raw_data) if isinstance(raw_data, dict) else payload

    raw_analysis = data.get("analysis")
    analysis = cast(dict[str, Any], raw_analysis) if isinstance(raw_analysis, dict) else {}

    raw_metadata = data.get("metadata")
    metadata = cast(dict[str, Any], raw_metadata) if isinstance(raw_metadata, dict) else {}

    return {
        "conversation_id": data.get("conversation_id"),
        "summary": analysis.get("transcript_summary"),
        "language": metadata.get("language"),
        "escalated": bool(metadata.get("escalated", False)),
    }
