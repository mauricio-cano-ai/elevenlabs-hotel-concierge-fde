from __future__ import annotations

from app.integrations.pms.base import PMSUnavailableError
from app.models import AvailabilityRequest, AvailabilityResponse


class CloudbedsAdapter:
    """Contract placeholder: intentionally requires real customer credentials/configuration."""

    def check_availability(self, request: AvailabilityRequest) -> AvailabilityResponse:
        raise PMSUnavailableError("Cloudbeds adapter is not configured in the public demo")
