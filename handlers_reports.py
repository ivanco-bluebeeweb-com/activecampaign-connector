"""Value-add health report for ActiveCampaign Connector."""
from __future__ import annotations

from imperal_sdk import ActionResult

import activecampaign_client as ac
from app import chat
from handlers_connection import resolve_or_error
from schemas import AuditActiveCampaignAccountParams, ActiveCampaignAccountReport


@chat.function(
    "audit_activecampaign_account",
    "Build an account snapshot with contact, list, campaign, automation, and deal counts.",
    action_type="read", chain_callable=True, data_model=ActiveCampaignAccountReport,
)
async def audit_activecampaign_account(ctx, params: AuditActiveCampaignAccountParams) -> ActionResult:
    """Read headline collection totals without changing ActiveCampaign data."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err:
        return err
    endpoints = {
        "contacts": "/contacts",
        "lists": "/lists",
        "campaigns": "/campaigns",
        "automations": "/automations",
        "deals": "/deals",
    }
    counts: dict[str, int] = {}
    try:
        for key, path in endpoints.items():
            payload = await ac.request(
                conn["api_url"], conn["access_token"], "GET", path,
                params={"limit": 1}, action=f"audit {key}",
            )
            counts[key] = int(payload.get("meta", {}).get("total", 0))
    except (ac.ClientFail, ValueError) as exc:
        if isinstance(exc, ac.ClientFail):
            return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
        return ActionResult.error("ActiveCampaign returned an invalid total.", code=ac.AC_RESPONSE_UNEXPECTED)
    return ActionResult.success(ActiveCampaignAccountReport(
        total_contacts=counts["contacts"],
        total_lists=counts["lists"],
        total_campaigns=counts["campaigns"],
        total_automations=counts["automations"],
        total_deals=counts["deals"],
    ), summary="Activecampaign account audit ready.")
