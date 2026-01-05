"""
Authentication utilities for Databricks plugin.

Handles:
- PAT token retrieval from profiles
- Profile validation
- Token masking for display
"""

import os
import configparser
from pathlib import Path
from typing import Optional, Tuple

DATABRICKS_CFG_PATH = Path.home() / ".databrickscfg"


def get_token_for_profile(profile: str) -> Optional[str]:
    """
    Get the token for a specific profile.

    Args:
        profile: Profile name from ~/.databrickscfg

    Returns:
        Token string or None if not found
    """
    if not DATABRICKS_CFG_PATH.exists():
        return None

    config = configparser.ConfigParser()
    config.read(DATABRICKS_CFG_PATH)

    try:
        return config.get(profile, 'token')
    except (configparser.NoSectionError, configparser.NoOptionError):
        return None


def validate_profile(profile: str) -> Tuple[bool, str]:
    """
    Validate that a profile exists and has required configuration.

    Args:
        profile: Profile name to validate

    Returns:
        Tuple of (is_valid, message)
    """
    if not DATABRICKS_CFG_PATH.exists():
        return False, f"~/.databrickscfg not found. Run /db:setup to configure."

    config = configparser.ConfigParser()
    config.read(DATABRICKS_CFG_PATH)

    if not config.has_section(profile) and profile != 'DEFAULT':
        sections = config.sections()
        return False, f"Profile '{profile}' not found. Available: {', '.join(sections)}"

    try:
        host = config.get(profile, 'host')
        token = config.get(profile, 'token')
    except configparser.NoOptionError as e:
        return False, f"Profile '{profile}' missing required option: {e.option}"

    if not host:
        return False, f"Profile '{profile}' has empty host"

    if not token:
        return False, f"Profile '{profile}' has empty token"

    return True, f"Profile '{profile}' is valid"


def mask_token(token: str) -> str:
    """
    Mask a token for safe display.

    Args:
        token: Full token string

    Returns:
        Masked token showing only first 4 and last 4 characters
    """
    if not token or len(token) < 12:
        return "****"
    return f"{token[:4]}...{token[-4:]}"


def get_auth_header(profile: str) -> dict:
    """
    Get authentication headers for API requests.

    Args:
        profile: Profile name

    Returns:
        Dict with Authorization header
    """
    token = get_token_for_profile(profile)
    if not token:
        raise ValueError(f"No token found for profile '{profile}'")

    return {"Authorization": f"Bearer {token}"}
