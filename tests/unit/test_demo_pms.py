from datetime import date, timedelta

from app.integrations.pms.demo import DemoPMSAdapter
from app.models import AvailabilityRequest


def test_demo_pms_returns_deterministic_matching_options() -> None:
    adapter = DemoPMSAdapter()
    check_in = date.today() + timedelta(days=7)
    request = AvailabilityRequest(
        check_in=check_in,
        check_out=check_in + timedelta(days=2),
        adults=2,
        children=0,
    )

    first = adapter.check_availability(request)
    second = adapter.check_availability(request)

    assert first.request_id != second.request_id
    assert first.options == second.options
    assert first.available is True
    assert [room.room_type for room in first.options] == [
        "Deluxe King",
        "Junior Suite",
        "Family Suite",
    ]
    assert first.options[0].nightly_rate_mxn == 2400
    assert first.options[0].base_total_mxn == 4800
