#!/usr/bin/env python3
"""
db_warehouses.py - Manage Databricks SQL warehouses

Usage:
    db_warehouses.py list [-p PROFILE] [-o FORMAT] [--state STATE]
    db_warehouses.py get WAREHOUSE_ID [-p PROFILE] [-o FORMAT]
    db_warehouses.py start WAREHOUSE_ID [-p PROFILE] [--wait]
    db_warehouses.py stop WAREHOUSE_ID [-p PROFILE] [--wait]

Examples:
    db_warehouses.py list -p DEV
    db_warehouses.py list -p PROD --state RUNNING
    db_warehouses.py start abc123 -p DEV --wait
"""

import argparse
import sys
import time
from pathlib import Path

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))

from _lib.config import get_workspace_client, get_default_profile
from _lib.auth import validate_profile
from _lib.output import format_output, print_error, print_success


def cmd_list(args):
    """List all SQL warehouses."""
    w = get_workspace_client(args.profile)

    warehouses = list(w.warehouses.list())

    # Filter by state if requested
    if args.state:
        warehouses = [
            wh for wh in warehouses
            if wh.state and wh.state.value.upper() == args.state.upper()
        ]

    if not warehouses:
        print("No SQL warehouses found")
        return 0

    # Format for output
    data = []
    for wh in warehouses:
        data.append({
            'id': wh.id,
            'name': wh.name,
            'state': wh.state.value if wh.state else 'UNKNOWN',
            'size': wh.cluster_size or 'N/A',
            'type': 'Serverless' if wh.enable_serverless_compute else 'Classic',
            'auto_stop': f"{wh.auto_stop_mins}m" if wh.auto_stop_mins else 'Never',
        })

    print(format_output(data, args.output))
    return 0


def cmd_get(args):
    """Get warehouse details."""
    w = get_workspace_client(args.profile)

    try:
        warehouse = w.warehouses.get(id=args.warehouse_id)

        if args.output == "json":
            print(format_output(warehouse, "json"))
        else:
            data = {
                'Warehouse ID': warehouse.id,
                'Name': warehouse.name,
                'State': warehouse.state.value if warehouse.state else 'UNKNOWN',
                'Size': warehouse.cluster_size or 'N/A',
                'Min Clusters': warehouse.min_num_clusters or 1,
                'Max Clusters': warehouse.max_num_clusters or 1,
                'Auto Stop': f"{warehouse.auto_stop_mins} min" if warehouse.auto_stop_mins else 'Never',
                'Type': 'Serverless' if warehouse.enable_serverless_compute else 'Classic',
                'Creator': warehouse.creator_name or 'N/A',
            }
            for key, value in data.items():
                print(f"{key}: {value}")

        return 0
    except Exception as e:
        print_error(f"Failed to get warehouse: {e}")
        return 1


def cmd_start(args):
    """Start a SQL warehouse."""
    w = get_workspace_client(args.profile)

    print(f"Starting warehouse {args.warehouse_id}...")

    try:
        if args.wait:
            w.warehouses.start_and_wait(id=args.warehouse_id)
            print_success(f"Warehouse {args.warehouse_id} is now RUNNING")
        else:
            w.warehouses.start(id=args.warehouse_id)
            print_success(f"Start command sent for warehouse {args.warehouse_id}")

        return 0
    except Exception as e:
        print_error(f"Failed to start warehouse: {e}")
        return 1


def cmd_stop(args):
    """Stop a SQL warehouse."""
    w = get_workspace_client(args.profile)

    print(f"Stopping warehouse {args.warehouse_id}...")

    try:
        w.warehouses.stop(id=args.warehouse_id)

        if args.wait:
            # Poll until stopped
            for _ in range(60):  # Max 5 minutes
                warehouse = w.warehouses.get(id=args.warehouse_id)
                if warehouse.state and warehouse.state.value == "STOPPED":
                    break
                time.sleep(5)

        print_success(f"Warehouse {args.warehouse_id} stopped")
        return 0
    except Exception as e:
        print_error(f"Failed to stop warehouse: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Manage Databricks SQL warehouses"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments
    def add_common_args(p):
        p.add_argument(
            "-p", "--profile",
            default=None,
            help="Databricks profile"
        )

    # list command
    list_parser = subparsers.add_parser("list", help="List warehouses")
    add_common_args(list_parser)
    list_parser.add_argument(
        "-o", "--output",
        choices=["table", "json", "csv"],
        default="table"
    )
    list_parser.add_argument(
        "--state",
        help="Filter by state (RUNNING, STOPPED, STARTING, etc.)"
    )

    # get command
    get_parser = subparsers.add_parser("get", help="Get warehouse details")
    get_parser.add_argument("warehouse_id", help="Warehouse ID")
    add_common_args(get_parser)
    get_parser.add_argument(
        "-o", "--output",
        choices=["table", "json"],
        default="table"
    )

    # start command
    start_parser = subparsers.add_parser("start", help="Start a warehouse")
    start_parser.add_argument("warehouse_id", help="Warehouse ID")
    add_common_args(start_parser)
    start_parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for warehouse to be running"
    )

    # stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a warehouse")
    stop_parser.add_argument("warehouse_id", help="Warehouse ID")
    add_common_args(stop_parser)
    stop_parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for warehouse to stop"
    )

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
    if args.command == "list":
        return cmd_list(args)
    elif args.command == "get":
        return cmd_get(args)
    elif args.command == "start":
        return cmd_start(args)
    elif args.command == "stop":
        return cmd_stop(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
