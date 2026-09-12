# FDE Case Study — Hotel Overflow Receptionist

## 1. Requirement
A hotel wants fewer lost reservation opportunities without replacing its front desk or handing payment risk to an AI agent.

## 2. Discovery → scope
The highest-value V1 is narrow: FAQ, availability, quote, lead capture, booking link, and escalation. Payment and reservation mutation are explicitly excluded.

## 3. Architecture decision
Use ElevenAgents for the conversation layer and a Python integration service for deterministic hotel operations. This avoids rebuilding voice infrastructure and gives the customer a clean boundary around PMS access, credentials, auditing, and business rules.

## 4. Reliability decisions
- prices are calculated in code, not by the model;
- side effects require idempotency keys;
- post-call events are HMAC verified and deduplicated;
- real PMS adapters fail closed until configured;
- errors are safe for agent consumption;
- conversation IDs correlate platform and application events.

## 5. Delivery strategy
Start with deterministic demo inventory to validate the complete conversation and integration contract. For a pilot, replace only the `PMSAdapter`, add customer-specific auth/rate-limit behavior, configure the live ElevenAgent, then run the same evaluation catalog against staging before traffic.

## 6. Success definition
The system succeeds when it recovers qualified booking intent accurately and hands the guest/staff a valid next step. A flashy conversation that invents a price or claims a false booking is a failure.

## 7. Why this is an FDE artifact
The code is only half the work. The artifact also captures discovery, scope boundaries, customer-risk tradeoffs, failure handling, rollout sequence, and measurable outcomes—the pieces required to own a strategic deployment end to end.
