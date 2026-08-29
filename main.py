"""Entrypoint for ActiveCampaign Connector validation and deployment."""
import os
import sys

_EXT_DIR = os.path.dirname(os.path.abspath(__file__))
if _EXT_DIR not in sys.path:
    sys.path.insert(0, _EXT_DIR)

for _mod in (
    "app", "schemas", "activecampaign_client", "handlers_connection",
    "handlers_entities", "handlers_reports", "panels", "panels_settings",
):
    sys.modules.pop(_mod, None)

from app import ext, chat  # noqa: E402,F401
import handlers_connection  # noqa: E402,F401
import handlers_entities  # noqa: E402,F401
import handlers_reports  # noqa: E402,F401
import panels  # noqa: E402,F401
import panels_settings  # noqa: E402,F401
