from __future__ import annotations

from app.models import LeadCaptureRequest, LeadCaptureResponse
from app.persistence.repositories import LeadRepository


class LeadService:
    def __init__(self, repository: LeadRepository) -> None:
        self.repository = repository

    def capture(self, request: LeadCaptureRequest) -> LeadCaptureResponse:
        return self.repository.capture(request)
