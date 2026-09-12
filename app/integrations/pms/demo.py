from __future__ import annotations

from app.models import AvailabilityRequest, AvailabilityResponse, RoomOption


class DemoPMSAdapter:
    _rooms = (
        ("Deluxe King", 2400, 2, True),
        ("Junior Suite", 3200, 4, True),
        ("Family Suite", 4100, 6, False),
    )

    def check_availability(self, request: AvailabilityRequest) -> AvailabilityResponse:
        nights = (request.check_out - request.check_in).days
        party = request.adults + request.children
        options = []
        for room_type, nightly, capacity, refundable in self._rooms:
            if party > capacity:
                continue
            if request.room_type and request.room_type.casefold() != room_type.casefold():
                continue
            options.append(
                RoomOption(
                    room_type=room_type,
                    nightly_rate_mxn=nightly,
                    base_total_mxn=nightly * nights,
                    max_guests=capacity,
                    refundable=refundable,
                )
            )
        return AvailabilityResponse(
            available=bool(options),
            options=options,
            policy_notes=[
                "Demo inventory is deterministic and is not connected to a live PMS.",
                "A booking link does not confirm a reservation.",
            ],
        )
