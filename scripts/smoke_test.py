from __future__ import annotations

import sys
from pathlib import Path
from datetime import date, timedelta

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import create_app


def main() -> int:
    app = create_app(database_url="sqlite+pysqlite:///:memory:", tool_api_key="smoke")
    client = TestClient(app)
    if client.get("/healthz").json() != {"status": "ok"}:
        return 1
    check_in = date.today() + timedelta(days=7)
    response = client.post(
        "/v1/tools/check-availability",
        headers={"Authorization": "Bearer smoke"},
        json={
            "check_in": check_in.isoformat(),
            "check_out": (check_in + timedelta(days=2)).isoformat(),
            "adults": 2,
            "children": 0,
            "conversation_id": "smoke-conversation",
        },
    )
    if response.status_code != 200 or not response.json().get("available"):
        return 2
    print("smoke: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
