# Demo Script

1. **Spanish FAQ:** “¿A qué hora es el check-in?” → answer from hotel knowledge.
2. **Availability:** request two guests for valid future dates → call `check_availability`.
3. **Quote:** select Deluxe King → use `quote_stay`, never freehand arithmetic.
4. **Lead:** provide name/contact → `capture_lead` with idempotency key.
5. **Booking:** request next step → `create_booking_link`; agent states no reservation is confirmed yet.
6. **Language switch:** continue in English without losing dates/party context.
7. **Payment boundary:** offer card number → agent refuses to collect it.
8. **Handoff:** “Quiero hablar con recepción” → request/transfer to staff path.
9. **Failure:** simulate PMS timeout → no invented availability, offer escalation.
10. **Post-call:** deliver signed event twice → first processed, second `duplicate_ignored`.
