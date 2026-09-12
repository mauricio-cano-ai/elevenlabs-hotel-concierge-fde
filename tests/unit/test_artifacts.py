import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_tool_contracts_are_valid_json_with_six_tools() -> None:
    data = json.loads((ROOT / "agent/tool-contracts.json").read_text())
    assert len(data["tools"]) == 6
    assert {tool["name"] for tool in data["tools"]} == {
        "check_availability",
        "quote_stay",
        "capture_lead",
        "create_booking_link",
        "request_handoff",
        "hotel_information",
    }


def test_eval_catalog_contains_twelve_named_scenarios() -> None:
    data = yaml.safe_load((ROOT / "evals/scenarios.yaml").read_text())
    assert len(data["scenarios"]) == 12
    assert all(item["id"] and item["expected"] for item in data["scenarios"])


def test_prompt_contains_safety_invariants() -> None:
    prompt = (ROOT / "agent/prompt.md").read_text().casefold()
    for phrase in [
        "never claim a reservation is confirmed",
        "never process payment",
        "availability and pricing require tools",
        "human handoff",
    ]:
        assert phrase in prompt
