from datetime import date, timedelta

from app.config import Settings
from app.models import BookingLinkRequest, QuoteRequest
from app.services.booking_links import BookingLinkService
from app.services.quoting import QuoteService


def test_quote_is_deterministic_and_never_model_calculated() -> None:
    service = QuoteService()
    request = QuoteRequest(room_type="Deluxe King", nightly_rate_mxn=2400, nights=3)
    quote = service.quote(request)
    assert quote.base_total_mxn == 7200
    assert quote.currency == "MXN"


def test_booking_link_contains_safe_stay_parameters_and_no_reservation_claim() -> None:
    service = BookingLinkService(Settings(booking_base_url="https://book.example/start"))
    check_in = date.today() + timedelta(days=5)
    response = service.create(
        BookingLinkRequest(
            check_in=check_in,
            check_out=check_in + timedelta(days=2),
            adults=2,
            children=0,
            room_type="Deluxe King",
        )
    )
    assert response.booking_url.startswith("https://book.example/start?")
    assert "Deluxe+King" in response.booking_url
    assert response.reservation_created is False
    assert "confirmed" not in response.message.casefold()
