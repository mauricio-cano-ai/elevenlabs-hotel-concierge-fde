from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.models import (
    AvailabilityRequest,
    AvailabilityResponse,
    BookingLinkRequest,
    BookingLinkResponse,
    HandoffRequest,
    HandoffResponse,
    HotelInformationResponse,
    LeadCaptureRequest,
    LeadCaptureResponse,
    QuoteRequest,
    QuoteResponse,
)
from app.security.tool_auth import require_tool_auth

router = APIRouter(prefix="/v1/tools", dependencies=[Depends(require_tool_auth)])


@router.post("/check-availability", response_model=AvailabilityResponse)
def check_availability(payload: AvailabilityRequest, request: Request) -> AvailabilityResponse:
    return request.app.state.availability_service.check(payload)


@router.post("/quote-stay", response_model=QuoteResponse)
def quote_stay(payload: QuoteRequest, request: Request) -> QuoteResponse:
    return request.app.state.quote_service.quote(payload)


@router.post("/capture-lead", response_model=LeadCaptureResponse)
def capture_lead(payload: LeadCaptureRequest, request: Request) -> LeadCaptureResponse:
    return request.app.state.lead_service.capture(payload)


@router.post("/create-booking-link", response_model=BookingLinkResponse)
def create_booking_link(payload: BookingLinkRequest, request: Request) -> BookingLinkResponse:
    return request.app.state.booking_link_service.create(payload)


@router.post("/request-handoff", response_model=HandoffResponse)
def request_handoff(payload: HandoffRequest, request: Request) -> HandoffResponse:
    return request.app.state.handoff_service.request(payload)


@router.get("/hotel-information", response_model=HotelInformationResponse)
def hotel_information() -> HotelInformationResponse:
    return HotelInformationResponse(
        hotel_name="Casa Nopal Boutique Hotel",
        check_in_time="15:00",
        check_out_time="12:00",
        pets="Small pets are welcome in designated rooms with prior notice.",
        breakfast="Breakfast is served daily from 07:00 to 11:00.",
        parking="Complimentary on-site parking is available for registered guests.",
        address="Demo property, Puerto Vallarta, Jalisco, Mexico",
        amenities=["Wi-Fi", "Pool", "Air conditioning", "24/7 front desk escalation"],
    )
