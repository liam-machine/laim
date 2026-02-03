#!/usr/bin/env python3
"""SharePoint authentication using MSAL device code flow.

Uses the PnP Management Shell client ID which has Sites.FullControl.All pre-consented,
allowing access to all SharePoint sites without additional admin consent.

Usage:
    from _lib.auth import SharePointAuth

    auth = SharePointAuth(tenant="johnholland")
    token = auth.get_token()
    headers = auth.get_headers()
"""

import json
import os
from pathlib import Path
from typing import Optional

import msal

# PnP Management Shell - has Sites.FullControl.All pre-consented
PNP_CLIENT_ID = "9bc3ab49-b65d-410a-85ad-de819febfddc"

AUTHORITY = "https://login.microsoftonline.com/organizations"


class SharePointAuth:
    """SharePoint REST API authentication.

    Example:
        >>> auth = SharePointAuth(tenant="contoso")
        >>> token = auth.get_token()
        >>> headers = auth.get_headers()
        >>> response = requests.get(f"{auth.base_url}/_api/web", headers=headers)
    """

    def __init__(self, tenant: str = "johnholland"):
        """Initialize SharePoint auth.

        Args:
            tenant: SharePoint tenant name (e.g., "contoso" for contoso.sharepoint.com)
        """
        self.tenant = tenant
        self.resource = f"https://{tenant}.sharepoint.com"
        self.base_url = self.resource
        self.token_path = Path.home() / ".credentials" / f"sp_{tenant}_token.json"

        self._app: Optional[msal.PublicClientApplication] = None
        self._cache: Optional[msal.SerializableTokenCache] = None

    def _get_app(self) -> msal.PublicClientApplication:
        """Get or create MSAL app."""
        if self._app is None:
            self._cache = msal.SerializableTokenCache()

            # Load existing cache
            if self.token_path.exists():
                try:
                    self._cache.deserialize(self.token_path.read_text())
                except (json.JSONDecodeError, ValueError):
                    pass

            self._app = msal.PublicClientApplication(
                PNP_CLIENT_ID,
                authority=AUTHORITY,
                token_cache=self._cache
            )

        return self._app

    def _save_cache(self):
        """Save token cache to disk."""
        if self._cache and self._cache.has_state_changed:
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            self.token_path.write_text(self._cache.serialize())
            os.chmod(self.token_path, 0o600)

    def get_token(self, interactive: bool = True) -> Optional[str]:
        """Get access token for SharePoint.

        Args:
            interactive: If True, prompt for device code if needed.

        Returns:
            Access token string, or None if not authenticated.
        """
        scopes = [f"{self.resource}/.default"]
        app = self._get_app()

        # Try cached token first
        accounts = app.get_accounts()
        if accounts:
            result = app.acquire_token_silent(scopes, account=accounts[0])
            if result and "access_token" in result:
                self._save_cache()
                return result["access_token"]

        if not interactive:
            return None

        # Device code flow
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise RuntimeError(f"Device flow failed: {flow.get('error_description', flow)}")

        print("=" * 60)
        print(f"To authenticate for SharePoint ({self.tenant})")
        print(f"Visit: {flow['verification_uri']}")
        print(f"Enter code: {flow['user_code']}")
        print("=" * 60)

        result = app.acquire_token_by_device_flow(flow)
        if "access_token" in result:
            self._save_cache()
            print("Authentication successful!")
            return result["access_token"]

        raise RuntimeError(f"Authentication failed: {result.get('error_description', result)}")

    def get_headers(self) -> dict:
        """Get HTTP headers for SharePoint REST API requests."""
        token = self.get_token()
        if not token:
            raise ValueError("No token available - authenticate first")

        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=verbose",
            "Content-Type": "application/json;odata=verbose",
        }

    def clear_cache(self):
        """Clear token cache."""
        if self.token_path.exists():
            self.token_path.unlink()
        self._app = None
        self._cache = None


if __name__ == "__main__":
    import sys

    tenant = sys.argv[1] if len(sys.argv) > 1 else "johnholland"

    auth = SharePointAuth(tenant=tenant)
    token = auth.get_token(interactive=False)

    if token:
        print(f"Token cached for {tenant}.sharepoint.com")
    else:
        print(f"No cached token. Run with --auth to authenticate:")
        print(f"  python _lib/auth.py {tenant} --auth")

        if len(sys.argv) > 2 and sys.argv[2] == "--auth":
            auth.get_token(interactive=True)
