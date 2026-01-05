#!/usr/bin/env python3
"""
db_jobs.py - Manage Databricks jobs and runs

Usage:
    db_jobs.py list [-p PROFILE] [-o FORMAT] [--name NAME]
    db_jobs.py get JOB_ID [-p PROFILE] [-o FORMAT]
    db_jobs.py runs JOB_ID [-p PROFILE] [-o FORMAT] [--limit N]
    db_jobs.py run JOB_ID [-p PROFILE] [--wait] [--params JSON]
    db_jobs.py cancel RUN_ID [-p PROFILE]
    db_jobs.py run-output RUN_ID [-p PROFILE]

Examples:
    db_jobs.py list -p DEV
    db_jobs.py list -p PROD --name "ETL"
    db_jobs.py run 12345 -p DEV --wait
    db_jobs.py runs 12345 -p DEV --limit 5
"""

import argparse
import json
import sys
from pathlib import Path

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))

from _lib.config import get_workspace_client, get_default_profile
from _lib.auth import validate_profile
from _lib.output import format_output, print_error, print_success


def cmd_list(args):
    """List all jobs."""
    w = get_workspace_client(args.profile)

    # Get jobs with optional name filter
    if args.name:
        jobs = list(w.jobs.list(name=args.name))
    else:
        jobs = list(w.jobs.list())

    if not jobs:
        print("No jobs found")
        return 0

    # Format for output
    data = []
    for job in jobs:
        settings = job.settings
        data.append({
            'job_id': job.job_id,
            'name': settings.name if settings else 'N/A',
            'created_time': job.created_time or 'N/A',
            'creator': job.creator_user_name or 'N/A',
        })

    print(format_output(data, args.output))
    return 0


def cmd_get(args):
    """Get job details."""
    w = get_workspace_client(args.profile)

    try:
        job = w.jobs.get(job_id=int(args.job_id))

        if args.output == "json":
            print(format_output(job, "json"))
        else:
            settings = job.settings
            data = {
                'Job ID': job.job_id,
                'Name': settings.name if settings else 'N/A',
                'Creator': job.creator_user_name or 'N/A',
                'Created': job.created_time or 'N/A',
            }

            # Add schedule if exists
            if settings and settings.schedule:
                data['Schedule'] = settings.schedule.quartz_cron_expression
                data['Timezone'] = settings.schedule.timezone_id

            for key, value in data.items():
                print(f"{key}: {value}")

        return 0
    except Exception as e:
        print_error(f"Failed to get job: {e}")
        return 1


def cmd_runs(args):
    """List runs for a job."""
    w = get_workspace_client(args.profile)

    try:
        runs = list(w.jobs.list_runs(
            job_id=int(args.job_id),
            limit=args.limit
        ))

        if not runs:
            print(f"No runs found for job {args.job_id}")
            return 0

        # Format for output
        data = []
        for run in runs:
            state = run.state
            data.append({
                'run_id': run.run_id,
                'start_time': run.start_time or 'N/A',
                'state': state.life_cycle_state.value if state and state.life_cycle_state else 'N/A',
                'result': state.result_state.value if state and state.result_state else 'N/A',
                'duration_ms': run.run_duration or 'N/A',
            })

        print(format_output(data, args.output))
        return 0
    except Exception as e:
        print_error(f"Failed to list runs: {e}")
        return 1


def cmd_run(args):
    """Trigger a job run."""
    w = get_workspace_client(args.profile)

    print(f"Triggering job {args.job_id}...")

    try:
        # Parse parameters if provided
        params = None
        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError:
                print_error("Invalid JSON for --params")
                return 1

        if args.wait:
            run = w.jobs.run_now_and_wait(
                job_id=int(args.job_id),
                notebook_params=params.get('notebook_params') if params else None,
            )
            state = run.state
            result = state.result_state.value if state and state.result_state else 'UNKNOWN'

            if result == "SUCCESS":
                print_success(f"Job {args.job_id} completed successfully (run_id: {run.run_id})")
            else:
                print_error(f"Job {args.job_id} finished with result: {result}")
                return 1
        else:
            run = w.jobs.run_now(
                job_id=int(args.job_id),
                notebook_params=params.get('notebook_params') if params else None,
            )
            print_success(f"Job triggered. Run ID: {run.run_id}")

        return 0
    except Exception as e:
        print_error(f"Failed to run job: {e}")
        return 1


def cmd_cancel(args):
    """Cancel a run."""
    w = get_workspace_client(args.profile)

    try:
        w.jobs.cancel_run(run_id=int(args.run_id))
        print_success(f"Run {args.run_id} cancelled")
        return 0
    except Exception as e:
        print_error(f"Failed to cancel run: {e}")
        return 1


def cmd_run_output(args):
    """Get output from a run."""
    w = get_workspace_client(args.profile)

    try:
        output = w.jobs.get_run_output(run_id=int(args.run_id))

        if output.notebook_output:
            result = output.notebook_output.result
            if result:
                print(result)
            else:
                print("No notebook output")
        elif output.error:
            print_error(output.error)
        else:
            print("No output available")

        return 0
    except Exception as e:
        print_error(f"Failed to get run output: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Manage Databricks jobs and runs"
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
    list_parser = subparsers.add_parser("list", help="List jobs")
    add_common_args(list_parser)
    list_parser.add_argument(
        "-o", "--output",
        choices=["table", "json", "csv"],
        default="table"
    )
    list_parser.add_argument(
        "--name",
        help="Filter by job name"
    )

    # get command
    get_parser = subparsers.add_parser("get", help="Get job details")
    get_parser.add_argument("job_id", help="Job ID")
    add_common_args(get_parser)
    get_parser.add_argument(
        "-o", "--output",
        choices=["table", "json"],
        default="table"
    )

    # runs command
    runs_parser = subparsers.add_parser("runs", help="List job runs")
    runs_parser.add_argument("job_id", help="Job ID")
    add_common_args(runs_parser)
    runs_parser.add_argument(
        "-o", "--output",
        choices=["table", "json", "csv"],
        default="table"
    )
    runs_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max runs to show (default: 10)"
    )

    # run command
    run_parser = subparsers.add_parser("run", help="Trigger a job run")
    run_parser.add_argument("job_id", help="Job ID")
    add_common_args(run_parser)
    run_parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait for job to complete"
    )
    run_parser.add_argument(
        "--params",
        help="Job parameters as JSON"
    )

    # cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel a run")
    cancel_parser.add_argument("run_id", help="Run ID")
    add_common_args(cancel_parser)

    # run-output command
    output_parser = subparsers.add_parser("run-output", help="Get run output")
    output_parser.add_argument("run_id", help="Run ID")
    add_common_args(output_parser)

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
        "runs": cmd_runs,
        "run": cmd_run,
        "cancel": cmd_cancel,
        "run-output": cmd_run_output,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
