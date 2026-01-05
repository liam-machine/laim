#!/usr/bin/env python3
"""
db_deploy.py - Databricks Asset Bundles (DAB) deployment.

Uses the Databricks CLI for bundle operations (SDK doesn't support bundles).

Usage:
    db_deploy.py validate [-t TARGET] [-p PROFILE]
    db_deploy.py deploy [-t TARGET] [-p PROFILE]
    db_deploy.py destroy [-t TARGET] [-p PROFILE]
    db_deploy.py run JOB_KEY [-t TARGET] [-p PROFILE]
    db_deploy.py summary [-t TARGET] [-p PROFILE]

Examples:
    db_deploy.py validate -t dev -p DEV
    db_deploy.py deploy -t prod -p PROD
    db_deploy.py run my_job -t dev -p DEV
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))

from _lib.config import get_default_profile
from _lib.auth import validate_profile
from _lib.output import print_error, print_success


def run_cli(cmd: list, profile: str) -> tuple[int, str, str]:
    """Run a Databricks CLI command."""
    # Add profile to command
    full_cmd = ['databricks'] + cmd + ['-p', profile]

    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 1, '', "Databricks CLI not found. Install with: pip install databricks-cli"


def cmd_validate(args):
    """Validate bundle configuration."""
    cmd = ['bundle', 'validate']
    if args.target:
        cmd.extend(['-t', args.target])

    print("Validating bundle...")
    code, stdout, stderr = run_cli(cmd, args.profile)

    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    if code == 0:
        print_success("Bundle validation passed")
    else:
        print_error("Bundle validation failed")

    return code


def cmd_deploy(args):
    """Deploy bundle to target environment."""
    cmd = ['bundle', 'deploy']
    if args.target:
        cmd.extend(['-t', args.target])

    print(f"Deploying bundle{' to ' + args.target if args.target else ''}...")
    code, stdout, stderr = run_cli(cmd, args.profile)

    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    if code == 0:
        print_success("Bundle deployed successfully")
    else:
        print_error("Bundle deployment failed")

    return code


def cmd_destroy(args):
    """Destroy deployed bundle resources."""
    cmd = ['bundle', 'destroy', '--auto-approve']
    if args.target:
        cmd.extend(['-t', args.target])

    print(f"Destroying bundle resources{' in ' + args.target if args.target else ''}...")
    code, stdout, stderr = run_cli(cmd, args.profile)

    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    if code == 0:
        print_success("Bundle resources destroyed")
    else:
        print_error("Failed to destroy bundle resources")

    return code


def cmd_run(args):
    """Run a job defined in the bundle."""
    cmd = ['bundle', 'run', args.job_key]
    if args.target:
        cmd.extend(['-t', args.target])

    print(f"Running bundle job '{args.job_key}'...")
    code, stdout, stderr = run_cli(cmd, args.profile)

    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    if code == 0:
        print_success(f"Job '{args.job_key}' completed")
    else:
        print_error(f"Job '{args.job_key}' failed")

    return code


def cmd_summary(args):
    """Show bundle deployment summary."""
    cmd = ['bundle', 'summary']
    if args.target:
        cmd.extend(['-t', args.target])

    code, stdout, stderr = run_cli(cmd, args.profile)

    if stdout:
        print(stdout)
    if stderr and code != 0:
        print(stderr, file=sys.stderr)

    return code


def main():
    parser = argparse.ArgumentParser(
        description="Databricks Asset Bundles (DAB) deployment"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments
    def add_common_args(p):
        p.add_argument("-p", "--profile", default=None, help="Databricks profile")
        p.add_argument("-t", "--target", help="Deployment target (e.g., dev, prod)")

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate bundle configuration")
    add_common_args(validate_parser)

    # deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy bundle")
    add_common_args(deploy_parser)

    # destroy command
    destroy_parser = subparsers.add_parser("destroy", help="Destroy deployed resources")
    add_common_args(destroy_parser)

    # run command
    run_parser = subparsers.add_parser("run", help="Run a bundle job")
    run_parser.add_argument("job_key", help="Job key from databricks.yml")
    add_common_args(run_parser)

    # summary command
    summary_parser = subparsers.add_parser("summary", help="Show deployment summary")
    add_common_args(summary_parser)

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
        "validate": cmd_validate,
        "deploy": cmd_deploy,
        "destroy": cmd_destroy,
        "run": cmd_run,
        "summary": cmd_summary,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
