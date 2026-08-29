"""Thin HTTP client for the ActiveCampaign API v3 + Api-Token auth.

Same "fail()-dict + ClientFail exception + generic request() helper"
shape as every other connector this session's *_client.py. Confirmed
against developers.activecampaign.com, 2026-08-29:

- Auth header: Api-Token: {access_token}
- Base URL: per-account, e.g. https://{account}.api-us1.com/api/3
  (user supplies this at connect time -- there is no shared hostname).
"""
from __future__ import annotations

from typing import Any

import httpx

AC_NOT_CONNECTED = "ACTIVECAMPAIGN_NOT_CONNECTED"
AC_UNAUTHORIZED = "ACTIVECAMPAIGN_UNAUTHORIZED"
AC_FORBIDDEN = "ACTIVECAMPAIGN_FORBIDDEN"
AC_NOT_FOUND = "ACTIVECAMPAIGN_NOT_FOUND"
AC_RATE_LIMITED = "ACTIVECAMPAIGN_RATE_LIMITED"
AC_BACKEND_ERROR = "ACTIVECAMPAIGN_BACKEND_ERROR"
AC_VALIDATION_FAILED = "ACTIVECAMPAIGN_VALIDATION_FAILED"
AC_RESPONSE_UNEXPECTED = "ACTIVECAMPAIGN_RESPONSE_UNEXPECTED"

_MESSAGES = {
    AC_NOT_CONNECTED: "No ActiveCampaign account connected. Connect one first.",
    AC_UNAUTHORIZED: "ActiveCampaign rejected the API key as invalid or expired.",
    AC_FORBIDDEN: "ActiveCampaign denied access to this resource.",
    AC_NOT_FOUND: "That ActiveCampaign record was not found.",
    AC_RATE_LIMITED: "ActiveCampaign rate-limited this request. Try again shortly.",
    AC_BACKEND_ERROR: "ActiveCampaign returned an error.",
    AC_VALIDATION_FAILED: "ActiveCampaign rejected the request as invalid.",
    AC_RESPONSE_UNEXPECTED: "ActiveCampaign returned an unexpected response shape.",
}


def fail(code: str, detail: str = "") -> dict:
    msg = _MESSAGES.get(code, "ActiveCampaign request failed.")
    if detail:
        msg = f"{msg} ({detail})"
    return {"code": code, "message": msg}


class ClientFail(Exception):
    def __init__(self, payload: dict):
        super().__init__(payload.get("message", "ActiveCampaign request failed."))
        self.payload = payload


def _status_to_code(status: int) -> str:
    if status == 401:
        return AC_UNAUTHORIZED
    if status == 403:
        return AC_FORBIDDEN
    if status == 404:
        return AC_NOT_FOUND
    if status == 429:
        return AC_RATE_LIMITED
    if status >= 500:
        return AC_BACKEND_ERROR
    if status >= 400:
        return AC_VALIDATION_FAILED
    return AC_RESPONSE_UNEXPECTED


async def request(api_url: str, access_token: str, method: str, path: str,
                   params: dict | None = None, json_body: Any = None,
                   action: str = "") -> dict:
    base = api_url.rstrip("/")
    url = f"{base}{path}"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.request(
            method, url, params=params, json=json_body,
            headers={"Api-Token": access_token, "Accept": "application/json"},
        )
    if resp.status_code >= 400:
        code = _status_to_code(resp.status_code)
        detail = f"{action or method + ' ' + path}: HTTP {resp.status_code}: {resp.text[:300]}"
        raise ClientFail(fail(code, detail))
    if resp.status_code == 204 or not resp.content:
        return {}
    try:
        return resp.json()
    except ValueError:
        raise ClientFail(fail(AC_RESPONSE_UNEXPECTED, resp.text[:300]))
