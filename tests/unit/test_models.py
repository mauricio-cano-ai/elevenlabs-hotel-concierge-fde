from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.models import AvailabilityRequest


def test_rejects_checkout_not_after_checkin() -> None:
    tomorrow = date.today() + timedelta(days=1)
    with pytest.raises(ValidationError):
        AvailabilityRequest(check_in=tomorrow, check_out=tomorrow, adults=2, children=0)


def test_rejects_past_checkin() -> None:
    yesterday = date.today() - timedelta(days=1)
    tomorrow = date.today() + timedelta(days=1)
    with pytest.raises(ValidationError):
        AvailabilityRequest(check_in=yesterday, check_out=tomorrow, adults=2, children=0)


def test_rejects_demo_stay_longer_than_30_nights() -> None:
    check_in = date.today() + timedelta(days=1)
    with pytest.raises(ValidationError):
        AvailabilityRequest(
            check_in=check_in,
            check_out=check_in + timedelta(days=31),
            adults=2,
            children=0,
        )
