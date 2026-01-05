"""
Databricks Plugin Shared Library

Provides common utilities for all Databricks scripts:
- config: Workspace configuration and SDK client creation
- auth: Authentication handling (PAT, OAuth, profiles)
- output: Formatting (table, JSON, CSV)
"""

from .config import (
    get_profiles,
    get_workspace_client,
    get_default_profile,
    load_plugin_config,
    get_profile_host,
)
from .output import format_output, format_table, format_json, format_csv
from .auth import get_token_for_profile, validate_profile

__all__ = [
    "get_profiles",
    "get_workspace_client",
    "get_default_profile",
    "load_plugin_config",
    "get_profile_host",
    "format_output",
    "format_table",
    "format_json",
    "format_csv",
    "get_token_for_profile",
    "validate_profile",
]
