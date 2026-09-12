from __future__ import annotations

from app.integrations.pms.base import PMSAdapter
from app.models import AvailabilityRequest, AvailabilityResponse


class AvailabilityService:
    def __init__(self, adapter: PMSAdapter) -> None:
        self.adapter = adapter

    def check(self, request: AvailabilityRequest) -> AvailabilityResponse:
        return self.adapter.check_availability(request)
