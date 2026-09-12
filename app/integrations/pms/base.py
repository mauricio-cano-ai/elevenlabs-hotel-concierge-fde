from __future__ import annotations

from typing import Protocol

from app.models import AvailabilityRequest, AvailabilityResponse


class PMSUnavailableError(RuntimeError):
    pass


class PMSTimeoutError(TimeoutError):
    pass


class PMSAdapter(Protocol):
    def check_availability(self, request: AvailabilityRequest) -> AvailabilityResponse: ...
