#!/usr/bin/env python3
"""
db_pipelines.py - Manage Delta Live Tables / Lakeflow pipelines.

Usage:
    db_pipelines.py list [-p PROFILE]
    db_pipelines.py get PIPELINE_ID [-p PROFILE]
    db_pipelines.py start PIPELINE_ID [-p PROFILE] [--wait] [--full-refresh]
    db_pipelines.py stop PIPELINE_ID [-p PROFILE]
    db_pipelines.py updates PIPELINE_ID [-p PROFILE] [--limit N]
    db_pipelines.py events PIPELINE_ID [-p PROFILE] [--limit N]

Examples:
    db_pipelines.py list -p DEV
    db_pipelines.py start abc123 -p DEV --wait
    db_pipelines.py updates abc123 -p DEV --limit 5
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
    """List all pipelines."""
    w = get_workspace_client(args.profile)

    pipelines = list(w.pipelines.list_pipelines())

    if not pipelines:
        print("No pipelines found")
        return 0

    data = []
    for p in pipelines:
        data.append({
            'pipeline_id': p.pipeline_id,
            'name': p.name or 'N/A',
            'state': p.state.value if p.state else 'UNKNOWN',
            'creator': p.creator_user_name or 'N/A',
        })

    print(format_output(data, args.output))
    return 0


def cmd_get(args):
    """Get pipeline details."""
    w = get_workspace_client(args.profile)

    try:
        pipeline = w.pipelines.get(pipeline_id=args.pipeline_id)
        p = pipeline.spec

        if args.output == "json":
            import json
            print(json.dumps({
                'pipeline_id': pipeline.pipeline_id,
                'name': p.name if p else None,
                'state': pipeline.state.value if pipeline.state else None,
                'target': p.target if p else None,
                'continuous': p.continuous if p else None,
                'development': p.development if p else None,
                'catalog': p.catalog if p else None,
                'creator': pipeline.creator_user_name,
                'latest_updates': [
                    {
                        'update_id': u.update_id,
                        'state': u.state.value if u.state else None,
                        'creation_time': u.creation_time,
                    }
                    for u in (pipeline.latest_updates or [])[:3]
                ]
            }, indent=2))
        else:
            print(f"Pipeline: {p.name if p else 'N/A'}")
            print(f"ID: {pipeline.pipeline_id}")
            print(f"State: {pipeline.state.value if pipeline.state else 'UNKNOWN'}")
            print(f"Target: {p.target if p else 'N/A'}")
            print(f"Catalog: {p.catalog if p else 'N/A'}")
            print(f"Continuous: {p.continuous if p else False}")
            print(f"Development: {p.development if p else False}")
            print(f"Creator: {pipeline.creator_user_name or 'N/A'}")

            if pipeline.latest_updates:
                print("\nRecent Updates:")
                for u in pipeline.latest_updates[:3]:
                    print(f"  - {u.update_id}: {u.state.value if u.state else 'UNKNOWN'}")

        return 0
    except Exception as e:
        print_error(f"Failed to get pipeline: {e}")
        return 1


def cmd_start(args):
    """Start a pipeline update."""
    w = get_workspace_client(args.profile)

    print(f"Starting pipeline {args.pipeline_id}...")

    try:
        response = w.pipelines.start_update(
            pipeline_id=args.pipeline_id,
            full_refresh=args.full_refresh
        )

        update_id = response.update_id
        print(f"Update started: {update_id}")

        if args.wait:
            print("Waiting for completion...")
            while True:
                update = w.pipelines.get_update(
                    pipeline_id=args.pipeline_id,
                    update_id=update_id
                )
                state = update.update.state.value if update.update and update.update.state else 'UNKNOWN'

                if state in ('COMPLETED', 'FAILED', 'CANCELED'):
                    if state == 'COMPLETED':
                        print_success(f"Pipeline update completed: {update_id}")
                    else:
                        print_error(f"Pipeline update {state.lower()}: {update_id}")
                        return 1
                    break

                print(f"  State: {state}...")
                time.sleep(10)

        return 0
    except Exception as e:
        print_error(f"Failed to start pipeline: {e}")
        return 1


def cmd_stop(args):
    """Stop a pipeline."""
    w = get_workspace_client(args.profile)

    print(f"Stopping pipeline {args.pipeline_id}...")

    try:
        w.pipelines.stop(pipeline_id=args.pipeline_id)
        print_success(f"Stop request sent for pipeline {args.pipeline_id}")
        return 0
    except Exception as e:
        print_error(f"Failed to stop pipeline: {e}")
        return 1


def cmd_updates(args):
    """List recent pipeline updates."""
    w = get_workspace_client(args.profile)

    try:
        updates = w.pipelines.list_updates(
            pipeline_id=args.pipeline_id,
            max_results=args.limit
        )

        if not updates.updates:
            print(f"No updates for pipeline {args.pipeline_id}")
            return 0

        data = []
        for u in updates.updates:
            data.append({
                'update_id': u.update_id,
                'state': u.state.value if u.state else 'UNKNOWN',
                'creation_time': u.creation_time or 'N/A',
                'cause': u.cause.value if u.cause else 'N/A',
            })

        print(format_output(data, args.output))
        return 0
    except Exception as e:
        print_error(f"Failed to list updates: {e}")
        return 1


def cmd_events(args):
    """Get pipeline events (for debugging)."""
    w = get_workspace_client(args.profile)

    try:
        events = w.pipelines.list_pipeline_events(
            pipeline_id=args.pipeline_id,
            max_results=args.limit
        )

        if not events.events:
            print(f"No events for pipeline {args.pipeline_id}")
            return 0

        data = []
        for e in events.events:
            data.append({
                'timestamp': e.timestamp or 'N/A',
                'level': e.level.value if e.level else 'N/A',
                'message': e.message or 'N/A',
                'event_type': e.event_type or 'N/A',
            })

        print(format_output(data, args.output))
        return 0
    except Exception as e:
        print_error(f"Failed to list events: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Manage Delta Live Tables / Lakeflow pipelines"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments
    def add_common_args(p):
        p.add_argument("-p", "--profile", default=None, help="Databricks profile")
        p.add_argument("-o", "--output", choices=["table", "json", "csv"], default="table")

    # list command
    list_parser = subparsers.add_parser("list", help="List pipelines")
    add_common_args(list_parser)

    # get command
    get_parser = subparsers.add_parser("get", help="Get pipeline details")
    get_parser.add_argument("pipeline_id", help="Pipeline ID")
    add_common_args(get_parser)

    # start command
    start_parser = subparsers.add_parser("start", help="Start a pipeline update")
    start_parser.add_argument("pipeline_id", help="Pipeline ID")
    start_parser.add_argument("--wait", action="store_true", help="Wait for completion")
    start_parser.add_argument("--full-refresh", action="store_true", help="Full refresh")
    add_common_args(start_parser)

    # stop command
    stop_parser = subparsers.add_parser("stop", help="Stop a pipeline")
    stop_parser.add_argument("pipeline_id", help="Pipeline ID")
    add_common_args(stop_parser)

    # updates command
    updates_parser = subparsers.add_parser("updates", help="List recent updates")
    updates_parser.add_argument("pipeline_id", help="Pipeline ID")
    updates_parser.add_argument("--limit", type=int, default=10, help="Max results")
    add_common_args(updates_parser)

    # events command
    events_parser = subparsers.add_parser("events", help="List pipeline events")
    events_parser.add_argument("pipeline_id", help="Pipeline ID")
    events_parser.add_argument("--limit", type=int, default=20, help="Max results")
    add_common_args(events_parser)

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
        "start": cmd_start,
        "stop": cmd_stop,
        "updates": cmd_updates,
        "events": cmd_events,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
