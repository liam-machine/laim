#!/usr/bin/env python3
"""
db_lakeview.py - Manage Lakeview dashboards.

Usage:
    db_lakeview.py list [-p PROFILE]
    db_lakeview.py get DASHBOARD_ID [-p PROFILE]
    db_lakeview.py publish DASHBOARD_ID [-p PROFILE]
    db_lakeview.py unpublish DASHBOARD_ID [-p PROFILE]
    db_lakeview.py trash DASHBOARD_ID [-p PROFILE]

Examples:
    db_lakeview.py list -p DEV
    db_lakeview.py get abc123 -p DEV
    db_lakeview.py publish abc123 -p DEV
"""

import argparse
import sys
from pathlib import Path

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))

from _lib.config import get_workspace_client, get_default_profile
from _lib.auth import validate_profile
from _lib.output import format_output, print_error, print_success


def cmd_list(args):
    """List all Lakeview dashboards."""
    w = get_workspace_client(args.profile)

    try:
        dashboards = list(w.lakeview.list())

        if not dashboards:
            print("No Lakeview dashboards found")
            return 0

        data = []
        for d in dashboards:
            data.append({
                'dashboard_id': d.dashboard_id,
                'display_name': d.display_name or 'N/A',
                'lifecycle_state': d.lifecycle_state.value if d.lifecycle_state else 'N/A',
                'path': d.path or 'N/A',
            })

        print(format_output(data, args.output))
        return 0
    except Exception as e:
        print_error(f"Failed to list dashboards: {e}")
        return 1


def cmd_get(args):
    """Get dashboard details."""
    w = get_workspace_client(args.profile)

    try:
        dashboard = w.lakeview.get(dashboard_id=args.dashboard_id)

        if args.output == "json":
            import json
            print(json.dumps({
                'dashboard_id': dashboard.dashboard_id,
                'display_name': dashboard.display_name,
                'path': dashboard.path,
                'lifecycle_state': dashboard.lifecycle_state.value if dashboard.lifecycle_state else None,
                'warehouse_id': dashboard.warehouse_id,
                'create_time': dashboard.create_time,
                'update_time': dashboard.update_time,
            }, indent=2))
        else:
            print(f"Dashboard: {dashboard.display_name or 'N/A'}")
            print(f"ID: {dashboard.dashboard_id}")
            print(f"Path: {dashboard.path or 'N/A'}")
            print(f"State: {dashboard.lifecycle_state.value if dashboard.lifecycle_state else 'N/A'}")
            print(f"Warehouse: {dashboard.warehouse_id or 'N/A'}")
            print(f"Created: {dashboard.create_time or 'N/A'}")
            print(f"Updated: {dashboard.update_time or 'N/A'}")

        return 0
    except Exception as e:
        print_error(f"Failed to get dashboard: {e}")
        return 1


def cmd_publish(args):
    """Publish a dashboard."""
    w = get_workspace_client(args.profile)

    try:
        w.lakeview.publish(dashboard_id=args.dashboard_id)
        print_success(f"Published dashboard: {args.dashboard_id}")
        return 0
    except Exception as e:
        print_error(f"Failed to publish dashboard: {e}")
        return 1


def cmd_unpublish(args):
    """Unpublish a dashboard."""
    w = get_workspace_client(args.profile)

    try:
        w.lakeview.unpublish(dashboard_id=args.dashboard_id)
        print_success(f"Unpublished dashboard: {args.dashboard_id}")
        return 0
    except Exception as e:
        print_error(f"Failed to unpublish dashboard: {e}")
        return 1


def cmd_trash(args):
    """Move dashboard to trash."""
    w = get_workspace_client(args.profile)

    try:
        w.lakeview.trash(dashboard_id=args.dashboard_id)
        print_success(f"Moved dashboard to trash: {args.dashboard_id}")
        return 0
    except Exception as e:
        print_error(f"Failed to trash dashboard: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Manage Lakeview dashboards"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments
    def add_common_args(p):
        p.add_argument("-p", "--profile", default=None, help="Databricks profile")
        p.add_argument("-o", "--output", choices=["table", "json", "csv"], default="table")

    # list command
    list_parser = subparsers.add_parser("list", help="List dashboards")
    add_common_args(list_parser)

    # get command
    get_parser = subparsers.add_parser("get", help="Get dashboard details")
    get_parser.add_argument("dashboard_id", help="Dashboard ID")
    add_common_args(get_parser)

    # publish command
    publish_parser = subparsers.add_parser("publish", help="Publish a dashboard")
    publish_parser.add_argument("dashboard_id", help="Dashboard ID")
    add_common_args(publish_parser)

    # unpublish command
    unpublish_parser = subparsers.add_parser("unpublish", help="Unpublish a dashboard")
    unpublish_parser.add_argument("dashboard_id", help="Dashboard ID")
    add_common_args(unpublish_parser)

    # trash command
    trash_parser = subparsers.add_parser("trash", help="Move dashboard to trash")
    trash_parser.add_argument("dashboard_id", help="Dashboard ID")
    add_common_args(trash_parser)

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
        "list": cmd_list,
        "get": cmd_get,
        "publish": cmd_publish,
        "unpublish": cmd_unpublish,
        "trash": cmd_trash,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
