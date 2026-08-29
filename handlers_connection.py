"""Connection lifecycle: connect (verify via GET /users/me), list,
disconnect.

Same "secrets-store list of dicts" shape as every other BYOK connector
this session's handlers_connection.py.
"""
from __future__ import annotations

import json
import uuid

from imperal_sdk import ActionResult

import activecampaign_client as ac
from app import chat
from schemas import (
    ConnectActiveCampaignParams, ConnectActiveCampaignResult,
    DisconnectActiveCampaignParams, DeleteResult,
    ActiveCampaignConnection, ConnectionList, NoParams,
)

_CONNECTIONS_SECRET = "activecampaign_connections"


async def _load_connections(ctx) -> list[dict]:
    raw = await ctx.secrets.get(_CONNECTIONS_SECRET)
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return []
    return data if isinstance(data, list) else []


async def _save_connections(ctx, connections: list[dict]) -> None:
    await ctx.secrets.set(_CONNECTIONS_SECRET, json.dumps(connections))


async def resolve_connection(ctx, connection_id: str = "") -> dict | None:
    connections = await _load_connections(ctx)
    if not connections:
        return None
    if connection_id:
        return next((c for c in connections if c.get("id") == connection_id), None)
    return connections[0]


async def resolve_or_error(ctx, connection_id: str = ""):
    conn = await resolve_connection(ctx, connection_id)
    if not conn:
        return None, ActionResult.error(
            "No ActiveCampaign account found. Connect one with connect_activecampaign first.",
            code=ac.AC_NOT_CONNECTED,
        )
    return conn, None


@chat.function(
    "connect_activecampaign",
    "Connect your own ActiveCampaign account by saving its API URL and API key, after checking they actually work.",
    action_type="write", chain_callable=True, event="activecampaign-connector.connect_activecampaign",
)
async def connect_activecampaign(ctx, params: ConnectActiveCampaignParams) -> ActionResult:
    """Verify the credentials via GET /users/me, then store them."""
    api_url = params.api_url.strip().rstrip("/")
    if not api_url.startswith("http"):
        api_url = f"https://{api_url}"
    # Accept either the account host or the exact API URL shown in Settings > Developer.
    if not api_url.endswith("/api/3"):
        api_url = f"{api_url}/api/3"
    try:
        data = await ac.request(api_url, params.access_token, "GET", "/users/me", action="verify credentials")
    except ac.ClientFail as exc:
        return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    connections = await _load_connections(ctx)
    connection_id = str(uuid.uuid4())
    connections.append({
        "id": connection_id,
        "label": params.label or "ActiveCampaign account",
        "api_url": api_url,
        "access_token": params.access_token,
    })
    await _save_connections(ctx, connections)
    return ActionResult.ok(ConnectActiveCampaignResult(
        connection_id=connection_id, label=params.label or "ActiveCampaign account", api_url=api_url,
    ))


@chat.function(
    "disconnect_activecampaign",
    "Disconnect an ActiveCampaign account: deletes the saved API URL/API key. Nothing in ActiveCampaign itself is changed.",
    action_type="write", chain_callable=True, event="activecampaign-connector.disconnect_activecampaign",
)
async def disconnect_activecampaign(ctx, params: DisconnectActiveCampaignParams) -> ActionResult:
    connections = await _load_connections(ctx)
    remaining = [c for c in connections if c.get("id") != params.connection_id]
    if len(remaining) == len(connections):
        return ActionResult.error("No connection found with that id.", code=ac.AC_NOT_FOUND)
    await _save_connections(ctx, remaining)
    return ActionResult.ok(DeleteResult(deleted=True, id=params.connection_id))


@chat.function(
    "list_connections",
    "List the connected ActiveCampaign accounts.",
    action_type="read", chain_callable=True, data_model=ConnectionList,
)
async def list_connections(ctx, params: NoParams) -> ActionResult:
    connections = await _load_connections(ctx)
    return ActionResult.ok(ConnectionList(connections=[
        ActiveCampaignConnection(id=c.get("id", ""), label=c.get("label", ""), api_url=c.get("api_url", ""))
        for c in connections
    ]))
