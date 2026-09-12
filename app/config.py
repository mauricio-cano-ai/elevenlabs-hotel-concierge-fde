from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ElevenLabs Hotel Concierge FDE"
    environment: str = "demo"
    tool_api_key: str = "demo-tool-key"
    elevenlabs_webhook_secret: str = "demo-webhook-secret"
    database_url: str = "sqlite:///./hotel_concierge.db"
    booking_base_url: str = "https://booking.example.test/start"
    max_stay_nights: int = 30
    webhook_tolerance_seconds: int = 300


@lru_cache
def get_settings() -> Settings:
    return Settings()
