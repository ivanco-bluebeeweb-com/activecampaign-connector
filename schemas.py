"""Pydantic param/result models for ActiveCampaign Connector.

Same "explicit ConnectionScoped mixin + one params + one result class per
@chat.function" shape as every other connector this session's schemas.py.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class NoParams(BaseModel):
    pass


class ConnectionScoped(BaseModel):
    connection_id: str = Field("", description="Which saved ActiveCampaign account to use. Omit if only one is connected.")


# ── Connection lifecycle ────────────────────────────────────────────────

class ConnectActiveCampaignParams(BaseModel):
    label: str = Field("", description="A friendly name for this account, e.g. 'Marketing team'.")
    api_url: str = Field(description="Your ActiveCampaign account URL or API URL, e.g. https://youraccount.api-us1.com/api/3 (Settings > Developer).")
    access_token: str = Field(description="Your ActiveCampaign API key (Settings > Developer).")


class ConnectActiveCampaignResult(BaseModel):
    connection_id: str = ""
    label: str = ""
    api_url: str = ""


class DisconnectActiveCampaignParams(BaseModel):
    connection_id: str = Field(description="The connection id to disconnect, from list_connections.")


class DeleteResult(BaseModel):
    deleted: bool = False
    id: str = ""


class ActiveCampaignConnection(BaseModel):
    id: str = ""
    label: str = ""
    api_url: str = ""


class ConnectionList(BaseModel):
    connections: list[ActiveCampaignConnection] = Field(default_factory=list)


# ── Contacts ──────────────────────────────────────────────────────────────

class ListContactsParams(ConnectionScoped):
    email: str = Field("", description="Filter to a contact with this exact email, if given.")
    limit: int = Field(20, description="Max number of contacts to return.")


class Contact(BaseModel):
    id: str = ""
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    phone: str = ""


class ContactList(BaseModel):
    contacts: list[Contact] = Field(default_factory=list)


class CreateContactParams(ConnectionScoped):
    email: str = Field(description="The contact's email address.")
    first_name: str = Field("", description="The contact's first name.")
    last_name: str = Field("", description="The contact's last name.")
    phone: str = Field("", description="The contact's phone number.")


class ContactCreateResult(BaseModel):
    contact_id: str = ""
    email: str = ""


class DeleteContactParams(ConnectionScoped):
    contact_id: str = Field(description="The contact id to delete, from list_contacts.")


class AddContactToListParams(ConnectionScoped):
    contact_id: str = Field(description="The contact id, from list_contacts.")
    list_id: str = Field(description="The list id to add the contact to, from list_lists.")


class ContactListMembershipResult(BaseModel):
    contact_id: str = ""
    list_id: str = ""
    status: str = ""


# ── Lists ─────────────────────────────────────────────────────────────────

class ListListsParams(ConnectionScoped):
    pass


class MailingList(BaseModel):
    id: str = ""
    name: str = ""
    stringid: str = ""


class MailingListList(BaseModel):
    lists: list[MailingList] = Field(default_factory=list)


class CreateListParams(ConnectionScoped):
    name: str = Field(description="The new list's name, e.g. 'Newsletter subscribers'.")
    sender_url: str = Field(description="The sender's website URL, required by ActiveCampaign for CAN-SPAM compliance.")
    sender_reminder: str = Field("You are receiving this email because you subscribed.", description="The reminder text shown to recipients about why they're receiving this email.")


class ListCreateResult(BaseModel):
    list_id: str = ""
    name: str = ""


# ── Campaigns ─────────────────────────────────────────────────────────────

class ListCampaignsParams(ConnectionScoped):
    status: str = Field("", description="Filter by campaign status, e.g. '0' (draft), '5' (sent). Leave empty for all.")


class Campaign(BaseModel):
    id: str = ""
    name: str = ""
    type: str = ""
    status: str = ""
    sdate: str = ""


class CampaignList(BaseModel):
    campaigns: list[Campaign] = Field(default_factory=list)


# ── Automations ───────────────────────────────────────────────────────────

class ListAutomationsParams(ConnectionScoped):
    pass


class Automation(BaseModel):
    id: str = ""
    name: str = ""
    status: str = ""
    entered: str = ""


class AutomationList(BaseModel):
    automations: list[Automation] = Field(default_factory=list)


# ── Deals ─────────────────────────────────────────────────────────────────

class ListDealsParams(ConnectionScoped):
    limit: int = Field(20, description="Max number of deals to return.")


class Deal(BaseModel):
    id: str = ""
    title: str = ""
    value: str = ""
    currency: str = ""
    status: str = ""


class DealList(BaseModel):
    deals: list[Deal] = Field(default_factory=list)


class CreateDealParams(ConnectionScoped):
    title: str = Field(description="The deal's title, e.g. 'Acme Corp -- Enterprise plan'.")
    value: int = Field(0, description="The deal's value in cents (e.g. 500000 for $5,000.00).")
    currency: str = Field("usd", description="The deal's currency code, e.g. 'usd'.")
    contact_id: str = Field("", description="The contact id to link this deal to, from list_contacts.")


class DealCreateResult(BaseModel):
    deal_id: str = ""
    title: str = ""


# ── Reports ───────────────────────────────────────────────────────────────

class AuditActiveCampaignAccountParams(ConnectionScoped):
    pass


class ActiveCampaignAccountReport(BaseModel):
    total_contacts: int = 0
    total_lists: int = 0
    total_campaigns: int = 0
    total_automations: int = 0
    total_deals: int = 0
