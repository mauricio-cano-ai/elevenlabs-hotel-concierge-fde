from __future__ import annotations

from datetime import date
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

Language = Literal["es", "en"]
Urgency = Literal["normal", "urgent"]


class AvailabilityRequest(BaseModel):
    check_in: date
    check_out: date
    adults: int = Field(ge=1, le=8)
    children: int = Field(default=0, ge=0, le=8)
    room_type: str | None = None
    conversation_id: str | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> AvailabilityRequest:
        if self.check_in < date.today():
            raise ValueError("check_in must not be in the past")
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be after check_in")
        if (self.check_out - self.check_in).days > 30:
            raise ValueError("stay exceeds demo limit of 30 nights")
        return self


class RoomOption(BaseModel):
    room_type: str
    nightly_rate_mxn: int
    base_total_mxn: int
    max_guests: int
    refundable: bool


class AvailabilityResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    available: bool
    options: list[RoomOption]
    tax_fee_disclosure: str = "Taxes and fees are not included in demo base totals."
    policy_notes: list[str] = Field(default_factory=list)


class QuoteRequest(BaseModel):
    room_type: str
    nightly_rate_mxn: int = Field(gt=0)
    nights: int = Field(ge=1, le=30)
    conversation_id: str | None = None


class QuoteResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    room_type: str
    nights: int
    nightly_rate_mxn: int
    base_total_mxn: int
    currency: Literal["MXN"] = "MXN"
    tax_fee_disclosure: str = "Taxes and fees are quoted separately by the booking engine."


class LeadCaptureRequest(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=128)
    conversation_id: str | None = None
    guest_name: str = Field(min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=254)
    language: Language = "es"
    check_in: date | None = None
    check_out: date | None = None
    adults: int | None = Field(default=None, ge=1, le=8)
    children: int | None = Field(default=None, ge=0, le=8)
    room_type: str | None = None
    consent_source: str = "voice_conversation"


class LeadCaptureResponse(BaseModel):
    lead_id: str
    created: bool
    status: Literal["captured"] = "captured"


class BookingLinkRequest(BaseModel):
    conversation_id: str | None = None
    check_in: date
    check_out: date
    adults: int = Field(ge=1, le=8)
    children: int = Field(default=0, ge=0, le=8)
    room_type: str | None = None


class BookingLinkResponse(BaseModel):
    booking_url: str
    reservation_created: Literal[False] = False
    message: str = "This link starts the booking flow; no reservation has been created."


class HandoffRequest(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=128)
    conversation_id: str | None = None
    reason: str = Field(min_length=3, max_length=300)
    urgency: Urgency = "normal"
    guest_contact: str | None = Field(default=None, max_length=254)
    context_summary: str = Field(min_length=1, max_length=1000)


class HandoffResponse(BaseModel):
    handoff_id: str
    created: bool
    state: Literal["requested"] = "requested"
    next_step_message: str = (
        "A staff member should follow up; the local demo does not claim a PSTN transfer."
    )


class HotelInformationResponse(BaseModel):
    hotel_name: str
    check_in_time: str
    check_out_time: str
    pets: str
    breakfast: str
    parking: str
    address: str
    amenities: list[str]


class ErrorDetail(BaseModel):
    code: str
    message: str
    retryable: bool = False


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
