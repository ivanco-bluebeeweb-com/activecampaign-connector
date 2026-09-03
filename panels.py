"""ActiveCampaign sidebar UI, following UI_INTERFACE_STANDARD.md.

All inputs have visible labels and contextual placeholders. Setup guidance is
kept solely in the modal; no duplicate static instructions live in the left
sidebar. Only validated DUI kwargs are used.
"""
from __future__ import annotations

from imperal_sdk import ui

from app import ext
import handlers_connection as h


def _settings_button() -> ui.UINode:
    return ui.Button(
        "App settings", variant="secondary", size="sm", full_width=True,
        icon="settings", on_click=ui.Call("__panel__activecampaign_settings"),
    )


def _connections_section(connections: list[dict]) -> ui.UINode:
    if not connections:
        return ui.Text("No ActiveCampaign accounts connected yet.", variant="caption")
    return ui.Stack(direction="v", gap=1, children=[
        ui.Text(c.get("label") or "ActiveCampaign account", variant="body")
        for c in connections
    ])


def _connect_form() -> ui.UINode:
    return ui.Stack(direction="v", gap=2, full_width=True, children=[
        ui.Button("Sign in with ActiveCampaign (OAuth)", variant="primary", size="sm", full_width=True, icon="login"),
        ui.Divider(),
        ui.Text("Or connect via Account API Key", variant="caption"),
        ui.Form(
        submit_label="Connect ActiveCampaign",
        action=ui.Call("connect_activecampaign"),
        children=[
            ui.Stack(direction="v", gap=2, children=[
                ui.Stack(direction="v", gap=1, children=[
                    ui.Text("Account label", variant="label"),
                    ui.Input(param_name="label", placeholder="e.g. Marketing team"),
                ]),
                ui.Stack(direction="v", gap=1, children=[
                    ui.Text("API URL", variant="label"),
                    ui.Input(param_name="api_url", placeholder="https://youraccount.api-us1.com/api/3"),
                ]),
                ui.Stack(direction="v", gap=1, children=[
                    ui.Text("API key", variant="label"),
                    ui.Input(param_name="access_token", placeholder="Paste the key from Settings > Developer"),
                ]),
            ]),
        ],
    )
    ])


def _help_modal() -> ui.UINode:
    return ui.Modal(
        trigger=ui.Button("How do I set this up?", variant="ghost", size="sm", full_width=True),
        title="Connect ActiveCampaign",
        children=[
            ui.Text("In ActiveCampaign, open Settings > Developer. Copy the API URL and API Key, then paste both here. The key is saved securely for this connection."),
        ],
    )


@ext.panel("activecampaign_sidebar", slot="left")
async def activecampaign_sidebar(ctx, **kwargs) -> object:
    connections = await h._load_connections(ctx)
    return ui.Stack(direction="v", gap=3, children=[
        ui.Text("ActiveCampaign", variant="heading"),
        _connections_section(connections),
        ui.Divider(),
        _connect_form(),
        _help_modal(),
        ui.Spacer(),
        _settings_button(),
    ])
