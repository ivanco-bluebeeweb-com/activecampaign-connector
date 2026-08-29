"""ActiveCampaign connection management in the dedicated App settings panel."""
from __future__ import annotations

from imperal_sdk import ui

from app import ext
import handlers_connection as h


@ext.panel("activecampaign_settings", slot="center")
async def activecampaign_settings(ctx, **kwargs) -> object:
    connections = await h._load_connections(ctx)
    children: list[ui.UINode] = [
        ui.Text("ActiveCampaign — App settings", variant="heading"),
        ui.Divider(),
    ]
    if not connections:
        children.append(ui.Text("No ActiveCampaign accounts connected yet.", variant="caption"))
    for c in connections:
        children.extend([
            ui.Text(c.get("label") or "ActiveCampaign account", variant="body"),
            ui.Text(c.get("api_url", ""), variant="caption"),
            ui.Button(
                "Disconnect", variant="danger", size="sm",
                on_click=ui.Call("disconnect_activecampaign", {"connection_id": c.get("id", "")}),
            ),
            ui.Divider(),
        ])
    return ui.Stack(direction="v", gap=2, children=children)
