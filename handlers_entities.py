"""Contacts, Lists, Campaigns, Automations, Deals for ActiveCampaign Connector.

Confirmed against developers.activecampaign.com API v3 conventions,
2026-08-29: GET/POST /contacts, GET /lists, POST /lists, GET /campaigns,
GET /automations, GET /deals, POST /deals.
"""
from __future__ import annotations

from imperal_sdk import ActionResult

import activecampaign_client as ac
from app import chat
from handlers_connection import resolve_or_error
from schemas import (
    ListContactsParams, ContactList, Contact,
    CreateContactParams, ContactCreateResult,
    ListListsParams, MailingListList, MailingList,
    CreateListParams, ListCreateResult,
    ListCampaignsParams, CampaignList, Campaign,
    ListAutomationsParams, AutomationList, Automation,
    ListDealsParams, DealList, Deal,
    CreateDealParams, DealCreateResult,
)


def _contact_entity(c: dict) -> Contact:
    return Contact(
        id=c.get("id", ""), email=c.get("email", ""),
        first_name=c.get("firstName", ""), last_name=c.get("lastName", ""),
        phone=c.get("phone", ""),
    )


def _list_entity(l: dict) -> MailingList:
    return MailingList(id=l.get("id", ""), name=l.get("name", ""), stringid=l.get("stringid", ""))


def _campaign_entity(c: dict) -> Campaign:
    return Campaign(id=c.get("id", ""), name=c.get("name", ""), status=str(c.get("status", "")), type=c.get("type", ""))


def _automation_entity(a: dict) -> Automation:
    return Automation(id=a.get("id", ""), name=a.get("name", ""), status=str(a.get("status", "")), entered=str(a.get("entered", "")))


def _deal_entity(d: dict) -> Deal:
    return Deal(id=d.get("id", ""), title=d.get("title", ""), value=str(d.get("value", "")), currency=d.get("currency", ""), status=str(d.get("status", "")))


@chat.function(
    "list_contacts",
    "List contacts in the connected ActiveCampaign account, optionally filtered by exact email.",
    action_type="read", chain_callable=True, data_model=ContactList,
)
async def list_contacts(ctx, params: ListContactsParams) -> ActionResult:
    """GET /contacts."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err:
        return err
    query: dict = {"limit": params.limit}
    if params.email:
        query["email"] = params.email
    try:
        data = await ac.request(conn["api_url"], conn["access_token"], "GET", "/contacts", params=query, action="list contacts")
    except ac.ClientFail as exc:
        return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    contacts = [_contact_entity(c) for c in data.get("contacts", [])]
    return ActionResult.ok(ContactList(contacts=contacts))


@chat.function(
    "create_contact",
    "Create a new contact in the connected ActiveCampaign account.",
    action_type="write", chain_callable=True, event="activecampaign-connector.create_contact",
    data_model=ContactCreateResult,
)
async def create_contact(ctx, params: CreateContactParams) -> ActionResult:
    """POST /contacts."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err:
        return err
    body = {"contact": {
        "email": params.email,
        "firstName": params.first_name,
        "lastName": params.last_name,
        "phone": params.phone,
    }}
    try:
        data = await ac.request(conn["api_url"], conn["access_token"], "POST", "/contacts", json_body=body, action="create contact")
    except ac.ClientFail as exc:
        return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    c = data.get("contact", {})
    return ActionResult.ok(ContactCreateResult(id=c.get("id", ""), email=c.get("email", "")))


@chat.function(
    "list_mailing_lists",
    "List mailing lists configured on the connected ActiveCampaign account.",
    action_type="read", chain_callable=True, data_model=MailingListList,
)
async def list_mailing_lists(ctx, params: ListListsParams) -> ActionResult:
    """GET /lists."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err:
        return err
    try:
        data = await ac.request(conn["api_url"], conn["access_token"], "GET", "/lists", params={"limit": params.limit}, action="list mailing lists")
    except ac.ClientFail as exc:
        return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    lists = [_list_entity(l) for l in data.get("lists", [])]
    return ActionResult.ok(MailingListList(lists=lists))


@chat.function(
    "create_mailing_list",
    "Create a new mailing list on the connected ActiveCampaign account.",
    action_type="write", chain_callable=True, event="activecampaign-connector.create_mailing_list",
    data_model=ListCreateResult,
)
async def create_mailing_list(ctx, params: CreateListParams) -> ActionResult:
    """POST /lists."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err:
        return err
    body = {"list": {
        "name": params.name,
        "stringid": params.stringid,
        "senderUrl": params.sender_url,
        "sender_reminder": params.sender_reminder,
    }}
    try:
        data = await ac.request(conn["api_url"], conn["access_token"], "POST", "/lists", json_body=body, action="create mailing list")
    except ac.ClientFail as exc:
        return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    l = data.get("list", {})
    return ActionResult.ok(ListCreateResult(id=l.get("id", ""), name=l.get("name", "")))


@chat.function(
    "list_campaigns",
    "List email campaigns (one-off sends) in the connected ActiveCampaign account.",
    action_type="read", chain_callable=True, data_model=CampaignList,
)
async def list_campaigns(ctx, params: ListCampaignsParams) -> ActionResult:
    """GET /campaigns."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err:
        return err
    try:
        data = await ac.request(conn["api_url"], conn["access_token"], "GET", "/campaigns", params={"limit": params.limit}, action="list campaigns")
    except ac.ClientFail as exc:
        return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    campaigns = [_campaign_entity(c) for c in data.get("campaigns", [])]
    return ActionResult.ok(CampaignList(campaigns=campaigns))


@chat.function(
    "list_automations",
    "List automations (multi-step nurture sequences) configured in the connected ActiveCampaign account.",
    action_type="read", chain_callable=True, data_model=AutomationList,
)
async def list_automations(ctx, params: ListAutomationsParams) -> ActionResult:
    """GET /automations."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err:
        return err
    try:
        data = await ac.request(conn["api_url"], conn["access_token"], "GET", "/automations", params={"limit": params.limit}, action="list automations")
    except ac.ClientFail as exc:
        return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    automations = [_automation_entity(a) for a in data.get("automations", [])]
    return ActionResult.ok(AutomationList(automations=automations))


@chat.function(
    "list_deals",
    "List sales pipeline deals in the connected ActiveCampaign account.",
    action_type="read", chain_callable=True, data_model=DealList,
)
async def list_deals(ctx, params: ListDealsParams) -> ActionResult:
    """GET /deals."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err:
        return err
    try:
        data = await ac.request(conn["api_url"], conn["access_token"], "GET", "/deals", params={"limit": params.limit}, action="list deals")
    except ac.ClientFail as exc:
        return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    deals = [_deal_entity(d) for d in data.get("deals", [])]
    return ActionResult.ok(DealList(deals=deals))


@chat.function(
    "create_deal",
    "Create a new sales pipeline deal in the connected ActiveCampaign account.",
    action_type="write", chain_callable=True, event="activecampaign-connector.create_deal",
    data_model=DealCreateResult,
)
async def create_deal(ctx, params: CreateDealParams) -> ActionResult:
    """POST /deals."""
    conn, err = await resolve_or_error(ctx, params.connection_id)
    if err:
        return err
    body = {"deal": {
        "title": params.title,
        "value": params.value,
        "currency": params.currency,
        "contact": params.contact_id,
    }}
    try:
        data = await ac.request(conn["api_url"], conn["access_token"], "POST", "/deals", json_body=body, action="create deal")
    except ac.ClientFail as exc:
        return ActionResult.error(exc.payload["message"], code=exc.payload["code"])
    d = data.get("deal", {})
    return ActionResult.ok(DealCreateResult(deal_id=d.get("id", ""), title=d.get("title", "")))
