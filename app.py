"""Extension declaration, secrets, lifecycle hooks.

WHY BYOK, same reasoning as most connectors this session -- the user's
own ActiveCampaign account (contacts, lists, campaigns, automations,
deals) is managed via their own static API key.

WHY A STATIC API KEY + PER-ACCOUNT BASE URL, CONFIRMED against
developers.activecampaign.com/reference/authentication and .../url.md,
2026-08-29: ActiveCampaign API v3 authenticates every request with a
single long-lived API key sent as the `Api-Token` header (found in
Account Settings > Developer). Unlike most APIs, there is no shared
hostname -- every account has its own base URL
`https://{youraccountname}.api-us1.com/api/3` (also shown on the same
Developer settings page), so this connector asks for BOTH the API URL
and the API key at connect time.

WHY EACH CONNECTION STORES api_url + access_token, DIFFERENT SHAPE FROM
MOST SIBLING CONNECTORS THIS SESSION (which store only access_token) --
ActiveCampaign's per-account base URL is not derivable from the key
itself.
"""
from __future__ import annotations

from imperal_sdk import ChatExtension, Extension

ext = Extension(
    "activecampaign-connector",
    version="0.1.0",
    display_name="ActiveCampaign",
    icon="icon.svg",
    capabilities=["activecampaign:read", "activecampaign:write"],
    description=(
        "Connect your own ActiveCampaign account (API URL + API key) to "
        "manage contacts, lists, campaigns, automations, and deals."
    ),
)

chat = ChatExtension(ext)


@ext.health_check
async def health_check(ctx) -> dict:
    """Fast configuration health; no third-party call -- just confirms at
    least one account connection is stored, same shape as Buildium's/Cin7
    Core's health_check."""
    import json as _json
    raw = await ctx.secrets.get("activecampaign_connections")
    try:
        count = len(_json.loads(raw)) if raw else 0
    except Exception:
        count = 0
    return {
        "healthy": True,
        "detail": (
            f"{count} ActiveCampaign account(s) connected." if count
            else "Not connected yet -- run connect_activecampaign."
        ),
    }
