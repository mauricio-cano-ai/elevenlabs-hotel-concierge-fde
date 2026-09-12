from __future__ import annotations

from app.models import HandoffRequest, HandoffResponse
from app.persistence.repositories import HandoffRepository


class HandoffService:
    def __init__(self, repository: HandoffRepository) -> None:
        self.repository = repository

    def request(self, request: HandoffRequest) -> HandoffResponse:
        return self.repository.request(request)
