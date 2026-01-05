#!/usr/bin/env python3
"""
db_secrets.py - Manage Databricks secret scopes and secrets.

Usage:
    db_secrets.py list-scopes [-p PROFILE]
    db_secrets.py create-scope NAME [-p PROFILE]
    db_secrets.py delete-scope NAME [-p PROFILE]
    db_secrets.py list SCOPE [-p PROFILE]
    db_secrets.py put SCOPE KEY [--value VALUE] [-p PROFILE]
    db_secrets.py delete SCOPE KEY [-p PROFILE]
    db_secrets.py acls SCOPE [-p PROFILE]

Examples:
    db_secrets.py list-scopes -p DEV
    db_secrets.py create-scope my-scope -p DEV
    db_secrets.py put my-scope api-key --value "secret123" -p DEV
    db_secrets.py list my-scope -p DEV
"""

import argparse
import sys
from pathlib import Path

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))

from _lib.config import get_workspace_client, get_default_profile
from _lib.auth import validate_profile
from _lib.output import format_output, print_error, print_success


def cmd_list_scopes(args):
    """List all secret scopes."""
    w = get_workspace_client(args.profile)

    scopes = list(w.secrets.list_scopes())

    if not scopes:
        print("No secret scopes found")
        return 0

    data = []
    for scope in scopes:
        data.append({
            'name': scope.name,
            'backend_type': scope.backend_type.value if scope.backend_type else 'DATABRICKS',
        })

    print(format_output(data, args.output))
    return 0


def cmd_create_scope(args):
    """Create a new secret scope."""
    w = get_workspace_client(args.profile)

    try:
        w.secrets.create_scope(scope=args.name)
        print_success(f"Created secret scope: {args.name}")
        return 0
    except Exception as e:
        print_error(f"Failed to create scope: {e}")
        return 1


def cmd_delete_scope(args):
    """Delete a secret scope."""
    w = get_workspace_client(args.profile)

    try:
        w.secrets.delete_scope(scope=args.name)
        print_success(f"Deleted secret scope: {args.name}")
        return 0
    except Exception as e:
        print_error(f"Failed to delete scope: {e}")
        return 1


def cmd_list(args):
    """List secrets in a scope (names only, values are not retrievable)."""
    w = get_workspace_client(args.profile)

    try:
        secrets = list(w.secrets.list_secrets(scope=args.scope))

        if not secrets:
            print(f"No secrets in scope '{args.scope}'")
            return 0

        data = []
        for secret in secrets:
            data.append({
                'key': secret.key,
                'last_updated': secret.last_updated_timestamp or 'N/A',
            })

        print(format_output(data, args.output))
        return 0
    except Exception as e:
        print_error(f"Failed to list secrets: {e}")
        return 1


def cmd_put(args):
    """Put a secret value."""
    w = get_workspace_client(args.profile)

    # Get value from argument or stdin
    value = args.value
    if not value:
        print("Enter secret value (press Enter when done):", file=sys.stderr)
        value = input()

    if not value:
        print_error("Secret value cannot be empty")
        return 1

    try:
        w.secrets.put_secret(
            scope=args.scope,
            key=args.key,
            string_value=value
        )
        print_success(f"Set secret '{args.key}' in scope '{args.scope}'")
        return 0
    except Exception as e:
        print_error(f"Failed to put secret: {e}")
        return 1


def cmd_delete(args):
    """Delete a secret."""
    w = get_workspace_client(args.profile)

    try:
        w.secrets.delete_secret(scope=args.scope, key=args.key)
        print_success(f"Deleted secret '{args.key}' from scope '{args.scope}'")
        return 0
    except Exception as e:
        print_error(f"Failed to delete secret: {e}")
        return 1


def cmd_acls(args):
    """List ACLs for a secret scope."""
    w = get_workspace_client(args.profile)

    try:
        acls = list(w.secrets.list_acls(scope=args.scope))

        if not acls:
            print(f"No ACLs configured for scope '{args.scope}'")
            return 0

        data = []
        for acl in acls:
            data.append({
                'principal': acl.principal,
                'permission': acl.permission.value if acl.permission else 'N/A',
            })

        print(format_output(data, args.output))
        return 0
    except Exception as e:
        print_error(f"Failed to list ACLs: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Manage Databricks secret scopes and secrets"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments
    def add_common_args(p):
        p.add_argument("-p", "--profile", default=None, help="Databricks profile")
        p.add_argument("-o", "--output", choices=["table", "json", "csv"], default="table")

    # list-scopes command
    list_scopes_parser = subparsers.add_parser("list-scopes", help="List all secret scopes")
    add_common_args(list_scopes_parser)

    # create-scope command
    create_scope_parser = subparsers.add_parser("create-scope", help="Create a secret scope")
    create_scope_parser.add_argument("name", help="Scope name")
    add_common_args(create_scope_parser)

    # delete-scope command
    delete_scope_parser = subparsers.add_parser("delete-scope", help="Delete a secret scope")
    delete_scope_parser.add_argument("name", help="Scope name")
    add_common_args(delete_scope_parser)

    # list command
    list_parser = subparsers.add_parser("list", help="List secrets in a scope")
    list_parser.add_argument("scope", help="Scope name")
    add_common_args(list_parser)

    # put command
    put_parser = subparsers.add_parser("put", help="Put a secret value")
    put_parser.add_argument("scope", help="Scope name")
    put_parser.add_argument("key", help="Secret key")
    put_parser.add_argument("--value", help="Secret value (or enter interactively)")
    add_common_args(put_parser)

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a secret")
    delete_parser.add_argument("scope", help="Scope name")
    delete_parser.add_argument("key", help="Secret key")
    add_common_args(delete_parser)

    # acls command
    acls_parser = subparsers.add_parser("acls", help="List ACLs for a scope")
    acls_parser.add_argument("scope", help="Scope name")
    add_common_args(acls_parser)

    args = parser.parse_args()

    # Get profile
    profile = args.profile or get_default_profile()
    args.profile = profile

    # Validate profile
    is_valid, message = validate_profile(profile)
    if not is_valid:
        print_error(message)
        return 1

    # Dispatch
    commands = {
        "list-scopes": cmd_list_scopes,
        "create-scope": cmd_create_scope,
        "delete-scope": cmd_delete_scope,
        "list": cmd_list,
        "put": cmd_put,
        "delete": cmd_delete,
        "acls": cmd_acls,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
