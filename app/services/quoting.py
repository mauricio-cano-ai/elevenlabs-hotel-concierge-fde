from __future__ import annotations

from app.models import QuoteRequest, QuoteResponse


class QuoteService:
    def quote(self, request: QuoteRequest) -> QuoteResponse:
        return QuoteResponse(
            room_type=request.room_type,
            nights=request.nights,
            nightly_rate_mxn=request.nightly_rate_mxn,
            base_total_mxn=request.nightly_rate_mxn * request.nights,
        )
