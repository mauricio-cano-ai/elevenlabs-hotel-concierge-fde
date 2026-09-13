from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.api.ops import router as ops_router
from app.api.tools import router as tools_router
from app.api.webhooks import router as webhooks_router
from app.config import Settings
from app.integrations.pms.demo import DemoPMSAdapter
from app.persistence.database import Database
from app.persistence.repositories import (
    ConversationRepository,
    HandoffRepository,
    LeadRepository,
    WebhookEventRepository,
)
from app.services.availability import AvailabilityService
from app.services.booking_links import BookingLinkService
from app.services.handoff import HandoffService
from app.services.leads import LeadService
from app.services.quoting import QuoteService


def create_app(
    database_url: str | None = None,
    tool_api_key: str | None = None,
    webhook_secret: str | None = None,
) -> FastAPI:
    settings = Settings()
    updates: dict[str, object] = {}

    if database_url is not None:
        updates["database_url"] = database_url

    if tool_api_key is not None:
        updates["tool_api_key"] = tool_api_key

    if webhook_secret is not None:
        updates["elevenlabs_webhook_secret"] = webhook_secret
    if updates:
        settings = Settings.model_validate({**settings.model_dump(), **updates})
    db = Database(settings.database_url)
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.state.settings = settings
    app.state.db = db
    app.state.availability_service = AvailabilityService(DemoPMSAdapter())
    app.state.quote_service = QuoteService()
    app.state.booking_link_service = BookingLinkService(settings)
    app.state.lead_service = LeadService(LeadRepository(db))
    app.state.handoff_service = HandoffService(HandoffRepository(db))
    app.state.webhook_repository = WebhookEventRepository(db)
    app.state.conversation_repository = ConversationRepository(db)

    @app.exception_handler(HTTPException)
    async def http_error(_: Request, exc: HTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict) and "code" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": str(exc.detail),
                    "retryable": False,
                }
            },
        )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz() -> dict[str, str]:
        with db.engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        return {"status": "ready"}

    app.include_router(tools_router)
    app.include_router(webhooks_router)
    app.include_router(ops_router)
    return app


app = create_app()
