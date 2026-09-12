from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, Request


def require_tool_auth(request: Request, authorization: str | None = Header(default=None)) -> None:
    expected = request.app.state.settings.tool_api_key
    supplied = ""
    if authorization and authorization.startswith("Bearer "):
        supplied = authorization[7:]
    if not supplied or not hmac.compare_digest(supplied, expected):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "AUTH_ERROR",
                "message": "Invalid tool credential",
                "retryable": False,
            },
        )
