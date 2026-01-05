#!/usr/bin/env python3
"""
db_clusters.py - Manage Databricks Spark clusters

Usage:
    db_clusters.py list [-p PROFILE] [-o FORMAT] [--state STATE]
    db_clusters.py get CLUSTER_ID [-p PROFILE] [-o FORMAT]
    db_clusters.py start CLUSTER_ID [-p PROFILE] [--wait]
    db_clusters.py stop CLUSTER_ID [-p PROFILE] [--wait]
    db_clusters.py restart CLUSTER_ID [-p PROFILE] [--wait]

Examples:
    db_clusters.py list -p DEV
    db_clusters.py list -p PROD --state RUNNING
    db_clusters.py start abc123-def456 -p DEV --wait
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
    """List all clusters."""
    w = get_workspace_client(args.profile)

    clusters = list(w.clusters.list())

    # Filter by state if requested
    if args.state:
        clusters = [
            c for c in clusters
            if c.state and c.state.value.upper() == args.state.upper()
        ]

    if not clusters:
        print("No clusters found")
        return 0

    # Format for output
    data = []
    for c in clusters:
        data.append({
            'cluster_id': c.cluster_id,
            'cluster_name': c.cluster_name,
            'state': c.state.value if c.state else 'UNKNOWN',
            'creator': c.creator_user_name or 'N/A',
            'spark_version': c.spark_version or 'N/A',
        })

    print(format_output(data, args.output))
    return 0


def cmd_get(args):
    """Get cluster details."""
    w = get_workspace_client(args.profile)

    try:
        cluster = w.clusters.get(cluster_id=args.cluster_id)

        if args.output == "json":
            print(format_output(cluster, "json"))
        else:
            data = {
                'Cluster ID': cluster.cluster_id,
                'Name': cluster.cluster_name,
                'State': cluster.state.value if cluster.state else 'UNKNOWN',
                'State Message': cluster.state_message or 'N/A',
                'Creator': cluster.creator_user_name or 'N/A',
                'Spark Version': cluster.spark_version or 'N/A',
                'Node Type': cluster.node_type_id or 'N/A',
                'Driver Type': cluster.driver_node_type_id or cluster.node_type_id or 'N/A',
                'Num Workers': cluster.num_workers if cluster.num_workers else 'Autoscale',
                'Auto Terminate (min)': cluster.autotermination_minutes or 'Never',
            }
            for key, value in data.items():
                print(f"{key}: {value}")

        return 0
    except Exception as e:
        print_error(f"Failed to get cluster: {e}")
        return 1


def cmd_start(args):
    """Start a cluster."""
    w = get_workspace_client(args.profile)

    print(f"Starting cluster {args.cluster_id}...")

    try:
        if args.wait:
            w.clusters.start_and_wait(cluster_id=args.cluster_id)
            print_success(f"Cluster {args.cluster_id} is now RUNNING")
        else:
            w.clusters.start(cluster_id=args.cluster_id)
            print_success(f"Start command sent for cluster {args.cluster_id}")

        return 0
    except Exception as e:
        print_error(f"Failed to start cluster: {e}")
        return 1


def cmd_stop(args):
    """Stop (delete) a cluster."""
    w = get_workspace_client(args.profile)

    print(f"Stopping cluster {args.cluster_id}...")

    try:
        # Note: Databricks uses 'delete' to terminate/stop a cluster
        w.clusters.delete(cluster_id=args.cluster_id)

        if args.wait:
            # Poll until terminated
            for _ in range(60):  # Max 5 minutes
                cluster = w.clusters.get(cluster_id=args.cluster_id)
                if cluster.state and cluster.state.value == "TERMINATED":
                    break
                time.sleep(5)

        print_success(f"Cluster {args.cluster_id} stopped")
        return 0
    except Exception as e:
        print_error(f"Failed to stop cluster: {e}")
        return 1


def cmd_restart(args):
    """Restart a cluster."""
    w = get_workspace_client(args.profile)

    print(f"Restarting cluster {args.cluster_id}...")

    try:
        if args.wait:
            w.clusters.restart_and_wait(cluster_id=args.cluster_id)
            print_success(f"Cluster {args.cluster_id} restarted and is now RUNNING")
        else:
            w.clusters.restart(cluster_id=args.cluster_id)
            print_success(f"Restart command sent for cluster {args.cluster_id}")

        return 0
    except Exception as e:
        print_error(f"Failed to restart cluster: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Manage Databricks Spark clusters"
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
    list_parser = subparsers.add_parser("list", help="List clusters")
    add_common_args(list_parser)
    list_parser.add_argument(
        "-o", "--output",
        choices=["table", "json", "csv"],
        default="table"
    )
    list_parser.add_argument(
        "--state",
        help="Filter by state (RUNNING, TERMINATED, PENDING, etc.)"
    )

    # get command
    get_parser = subparsers.add_parser("get", help="Get cluster details")
    get_parser.add_argument("cluster_id", help="Cluster ID")
    add_common_args(get_parser)
    get_parser.add_argument(
        "-o", "--output",
        choices=["table", "json"],
        default="table"
    )

    # start command
    start_parser = subparsers.add_parser("start", help="Start a cluster")
    start_parser.add_argument("cluster_id", help="Cluster ID")
    add_common_args(start_parser)
    start_parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for cluster to be running"
    )

    # stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a cluster")
    stop_parser.add_argument("cluster_id", help="Cluster ID")
    add_common_args(stop_parser)
    stop_parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for cluster to terminate"
    )

    # restart command
    restart_parser = subparsers.add_parser("restart", help="Restart a cluster")
    restart_parser.add_argument("cluster_id", help="Cluster ID")
    add_common_args(restart_parser)
    restart_parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for cluster to be running"
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
    elif args.command == "restart":
        return cmd_restart(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
