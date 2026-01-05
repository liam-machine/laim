#!/usr/bin/env python3
"""
db_profiles.py - List and validate Databricks profiles

Usage:
    db_profiles.py list [--output FORMAT]
    db_profiles.py validate PROFILE
    db_profiles.py test PROFILE
"""

import argparse
import sys
from pathlib import Path

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))

from _lib.config import get_profiles, get_default_profile, list_profiles_table
from _lib.auth import validate_profile, mask_token
from _lib.output import format_output, print_error, print_success


def cmd_list(args):
    """List all available profiles."""
    profiles = get_profiles()

    if not profiles:
        print("No profiles found in ~/.databrickscfg")
        print("\nRun /db:setup to configure your first workspace.")
        return 1

    if args.output == "json":
        # Mask tokens in JSON output
        safe_profiles = {}
        for name, config in profiles.items():
            safe_profiles[name] = {
                'host': config.get('host'),
                'has_token': bool(config.get('token')),
                'cluster_id': config.get('cluster_id'),
            }
        print(format_output(safe_profiles, "json"))
    else:
        print(list_profiles_table())
        print(f"\nDefault profile: {get_default_profile()}")

    return 0


def cmd_validate(args):
    """Validate a profile configuration."""
    is_valid, message = validate_profile(args.profile)

    if is_valid:
        print_success(message)
        return 0
    else:
        print_error(message)
        return 1


def cmd_test(args):
    """Test a profile by making an API call."""
    try:
        from _lib.config import get_workspace_client
    except ImportError:
        print_error("databricks-sdk not installed. Install with: pip install databricks-sdk")
        return 1

    # First validate
    is_valid, message = validate_profile(args.profile)
    if not is_valid:
        print_error(message)
        return 1

    print(f"Testing profile '{args.profile}'...")

    try:
        w = get_workspace_client(args.profile)
        # Try to get current user
        user = w.current_user.me()
        print_success(f"Connected as: {user.user_name}")
        print(f"  Host: {w.config.host}")
        return 0
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Manage Databricks profiles"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    list_parser = subparsers.add_parser("list", help="List all profiles")
    list_parser.add_argument(
        "-o", "--output",
        choices=["table", "json"],
        default="table",
        help="Output format"
    )

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a profile")
    validate_parser.add_argument("profile", help="Profile name to validate")

    # test command
    test_parser = subparsers.add_parser("test", help="Test profile connection")
    test_parser.add_argument("profile", help="Profile name to test")

    args = parser.parse_args()

    if args.command == "list":
        return cmd_list(args)
    elif args.command == "validate":
        return cmd_validate(args)
    elif args.command == "test":
        return cmd_test(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
