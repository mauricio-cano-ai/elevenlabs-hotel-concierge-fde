from __future__ import annotations

from urllib.parse import urlencode

from app.config import Settings
from app.models import BookingLinkRequest, BookingLinkResponse


class BookingLinkService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create(self, request: BookingLinkRequest) -> BookingLinkResponse:
        params = {
            "check_in": request.check_in.isoformat(),
            "check_out": request.check_out.isoformat(),
            "adults": request.adults,
            "children": request.children,
        }
        if request.room_type:
            params["room_type"] = request.room_type
        url = f"{self.settings.booking_base_url}?{urlencode(params)}"
        return BookingLinkResponse(booking_url=url)
