"""
Configuration management for Databricks plugin.

Handles:
- Reading ~/.databrickscfg profiles
- Loading plugin-specific config from ~/.databricks-plugin/config.yaml
- Creating WorkspaceClient instances for any profile
"""

import os
import configparser
from pathlib import Path
from typing import Optional, Dict, Any, List

# Optional imports - gracefully handle missing dependencies
try:
    from databricks.sdk import WorkspaceClient
    HAS_SDK = True
except ImportError:
    HAS_SDK = False
    WorkspaceClient = None

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Standard paths
DATABRICKS_CFG_PATH = Path.home() / ".databrickscfg"
PLUGIN_CONFIG_PATH = Path.home() / ".databricks-plugin" / "config.yaml"


def get_profiles() -> Dict[str, Dict[str, str]]:
    """
    Read all profiles from ~/.databrickscfg.

    Returns:
        Dict mapping profile name to {'host': ..., 'token': ...}
    """
    profiles = {}

    if not DATABRICKS_CFG_PATH.exists():
        return profiles

    config = configparser.ConfigParser()
    config.read(DATABRICKS_CFG_PATH)

    for section in config.sections():
        profiles[section] = {
            'host': config.get(section, 'host', fallback=None),
            'token': config.get(section, 'token', fallback=None),
            'cluster_id': config.get(section, 'cluster_id', fallback=None),
        }

    # Also check DEFAULT section
    if config.has_section('DEFAULT') or config.defaults():
        profiles['DEFAULT'] = {
            'host': config.get('DEFAULT', 'host', fallback=None),
            'token': config.get('DEFAULT', 'token', fallback=None),
            'cluster_id': config.get('DEFAULT', 'cluster_id', fallback=None),
        }

    return profiles


def get_profile_host(profile: str) -> Optional[str]:
    """Get the host URL for a specific profile."""
    profiles = get_profiles()
    if profile in profiles:
        return profiles[profile].get('host')
    return None


def get_default_profile() -> str:
    """
    Determine the default profile to use.

    Priority:
    1. DATABRICKS_PROFILE environment variable
    2. Plugin config default_profile
    3. 'DEFAULT' if it exists
    4. First available profile
    """
    # Check environment variable
    env_profile = os.environ.get('DATABRICKS_PROFILE')
    if env_profile:
        return env_profile

    # Check plugin config
    plugin_config = load_plugin_config()
    if plugin_config and 'default_profile' in plugin_config:
        return plugin_config['default_profile']

    # Check for DEFAULT profile
    profiles = get_profiles()
    if 'DEFAULT' in profiles:
        return 'DEFAULT'

    # Return first available
    if profiles:
        return list(profiles.keys())[0]

    return 'DEFAULT'


def load_plugin_config() -> Optional[Dict[str, Any]]:
    """
    Load plugin-specific configuration from ~/.databricks-plugin/config.yaml.

    Returns:
        Dict with plugin config or None if not found
    """
    if not HAS_YAML:
        return None

    if not PLUGIN_CONFIG_PATH.exists():
        return None

    try:
        with open(PLUGIN_CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def get_workspace_client(profile: Optional[str] = None) -> 'WorkspaceClient':
    """
    Create a WorkspaceClient for the specified profile.

    Args:
        profile: Profile name from ~/.databrickscfg. If None, uses default.

    Returns:
        Configured WorkspaceClient instance

    Raises:
        ImportError: If databricks-sdk is not installed
        ValueError: If profile not found
    """
    if not HAS_SDK:
        raise ImportError(
            "databricks-sdk is not installed. Install with: pip install databricks-sdk"
        )

    if profile is None:
        profile = get_default_profile()

    # Validate profile exists
    profiles = get_profiles()
    if profile not in profiles and profile != 'DEFAULT':
        available = ', '.join(profiles.keys())
        raise ValueError(
            f"Profile '{profile}' not found in ~/.databrickscfg. "
            f"Available profiles: {available}"
        )

    return WorkspaceClient(profile=profile)


def list_profiles_table() -> str:
    """
    Generate a formatted table of available profiles.

    Returns:
        Markdown-formatted table string
    """
    profiles = get_profiles()

    if not profiles:
        return "No profiles found in ~/.databrickscfg"

    lines = ["| Profile | Host | Has Token |", "|---------|------|-----------|"]

    for name, config in profiles.items():
        host = config.get('host', 'N/A')
        # Shorten host for display
        if host and 'cloud.databricks.com' in host:
            host = host.replace('https://', '').replace('.cloud.databricks.com', '')
        has_token = 'Yes' if config.get('token') else 'No'
        lines.append(f"| {name} | {host} | {has_token} |")

    return '\n'.join(lines)
