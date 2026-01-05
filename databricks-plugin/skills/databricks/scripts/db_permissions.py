#!/usr/bin/env python3
"""
db_permissions.py - Manage object-level permissions and ACLs.

Usage:
    db_permissions.py get OBJECT_TYPE OBJECT_ID [-p PROFILE]
    db_permissions.py update OBJECT_TYPE OBJECT_ID --principal PRINCIPAL --level LEVEL [-p PROFILE]
    db_permissions.py levels OBJECT_TYPE [-p PROFILE]

Object Types:
    clusters, cluster-policies, directories, experiments,
    jobs, models, notebooks, pipelines, registered-models,
    repos, serving-endpoints, sql/warehouses

Examples:
    db_permissions.py get clusters abc123 -p DEV
    db_permissions.py update jobs 12345 --principal user@example.com --level CAN_MANAGE -p DEV
    db_permissions.py levels jobs -p DEV
"""

import argparse
import sys
from pathlib import Path

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))

from _lib.config import get_workspace_client, get_default_profile
from _lib.auth import validate_profile
from _lib.output import format_output, print_error, print_success


# Map CLI object types to SDK method prefixes
OBJECT_TYPE_MAP = {
    'clusters': 'cluster',
    'cluster-policies': 'cluster_policy',
    'directories': 'directory',
    'experiments': 'experiment',
    'jobs': 'job',
    'models': 'model',
    'notebooks': 'notebook',
    'pipelines': 'pipeline',
    'registered-models': 'registered_model',
    'repos': 'repo',
    'serving-endpoints': 'serving_endpoint',
    'sql/warehouses': 'sql_warehouse',
}


def cmd_get(args):
    """Get permissions for an object."""
    w = get_workspace_client(args.profile)

    object_type = args.object_type.lower()
    if object_type not in OBJECT_TYPE_MAP:
        print_error(f"Unknown object type: {object_type}")
        print(f"Valid types: {', '.join(OBJECT_TYPE_MAP.keys())}")
        return 1

    try:
        # Build method name dynamically
        method_name = f"get_{OBJECT_TYPE_MAP[object_type]}_permissions"
        method = getattr(w.permissions, method_name, None)

        if not method:
            # Try generic get
            result = w.permissions.get(
                object_type=object_type.replace('-', '_'),
                object_id=args.object_id
            )
        else:
            # Use specific method with appropriate parameter
            param_name = f"{OBJECT_TYPE_MAP[object_type]}_id"
            result = method(**{param_name: args.object_id})

        if not result.access_control_list:
            print(f"No permissions configured for {object_type}/{args.object_id}")
            return 0

        data = []
        for acl in result.access_control_list:
            user_name = acl.user_name or acl.group_name or acl.service_principal_name or 'N/A'
            for perm in (acl.all_permissions or []):
                data.append({
                    'principal': user_name,
                    'permission': perm.permission_level.value if perm.permission_level else 'N/A',
                    'inherited': 'Yes' if perm.inherited else 'No',
                })

        print(format_output(data, args.output))
        return 0
    except Exception as e:
        print_error(f"Failed to get permissions: {e}")
        return 1


def cmd_update(args):
    """Update permissions for an object."""
    w = get_workspace_client(args.profile)

    object_type = args.object_type.lower()
    if object_type not in OBJECT_TYPE_MAP:
        print_error(f"Unknown object type: {object_type}")
        return 1

    try:
        from databricks.sdk.service.iam import AccessControlRequest, PermissionLevel

        # Parse permission level
        try:
            level = PermissionLevel(args.level)
        except ValueError:
            print_error(f"Invalid permission level: {args.level}")
            print("Use 'levels' subcommand to see valid levels")
            return 1

        # Build access control request
        acl = AccessControlRequest(permission_level=level)

        # Determine principal type
        if '@' in args.principal:
            acl.user_name = args.principal
        elif args.principal.startswith('group:'):
            acl.group_name = args.principal.replace('group:', '')
        else:
            # Assume group if no @ symbol
            acl.group_name = args.principal

        # Build method name dynamically
        method_name = f"update_{OBJECT_TYPE_MAP[object_type]}_permissions"
        method = getattr(w.permissions, method_name, None)

        if method:
            param_name = f"{OBJECT_TYPE_MAP[object_type]}_id"
            method(**{param_name: args.object_id}, access_control_list=[acl])
        else:
            w.permissions.update(
                object_type=object_type.replace('-', '_'),
                object_id=args.object_id,
                access_control_list=[acl]
            )

        print_success(f"Updated permissions for {object_type}/{args.object_id}")
        return 0
    except Exception as e:
        print_error(f"Failed to update permissions: {e}")
        return 1


def cmd_levels(args):
    """List valid permission levels for an object type."""
    w = get_workspace_client(args.profile)

    object_type = args.object_type.lower()
    if object_type not in OBJECT_TYPE_MAP:
        print_error(f"Unknown object type: {object_type}")
        return 1

    try:
        method_name = f"get_{OBJECT_TYPE_MAP[object_type]}_permission_levels"
        method = getattr(w.permissions, method_name, None)

        if method:
            # Specific method exists
            try:
                result = method(**{f"{OBJECT_TYPE_MAP[object_type]}_id": "dummy"})
            except Exception:
                # Fall back to showing common levels
                result = None
        else:
            result = None

        if result and result.permission_levels:
            data = []
            for level in result.permission_levels:
                data.append({
                    'level': level.permission_level.value if level.permission_level else 'N/A',
                    'description': level.description or 'N/A',
                })
            print(format_output(data, args.output))
        else:
            # Show common permission levels
            print("Common permission levels:")
            common_levels = [
                ('CAN_VIEW', 'View only'),
                ('CAN_READ', 'Read access'),
                ('CAN_RUN', 'Can execute/run'),
                ('CAN_EDIT', 'Edit access'),
                ('CAN_MANAGE', 'Full management'),
                ('CAN_MANAGE_RUN', 'Manage runs'),
                ('IS_OWNER', 'Owner'),
            ]
            data = [{'level': l, 'description': d} for l, d in common_levels]
            print(format_output(data, args.output))

        return 0
    except Exception as e:
        print_error(f"Failed to get permission levels: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Manage object-level permissions and ACLs"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments
    def add_common_args(p):
        p.add_argument("-p", "--profile", default=None, help="Databricks profile")
        p.add_argument("-o", "--output", choices=["table", "json", "csv"], default="table")

    # get command
    get_parser = subparsers.add_parser("get", help="Get permissions for an object")
    get_parser.add_argument("object_type", help="Object type (e.g., clusters, jobs)")
    get_parser.add_argument("object_id", help="Object ID")
    add_common_args(get_parser)

    # update command
    update_parser = subparsers.add_parser("update", help="Update permissions")
    update_parser.add_argument("object_type", help="Object type")
    update_parser.add_argument("object_id", help="Object ID")
    update_parser.add_argument("--principal", required=True, help="User email or group name")
    update_parser.add_argument("--level", required=True, help="Permission level")
    add_common_args(update_parser)

    # levels command
    levels_parser = subparsers.add_parser("levels", help="List valid permission levels")
    levels_parser.add_argument("object_type", help="Object type")
    add_common_args(levels_parser)

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
        "get": cmd_get,
        "update": cmd_update,
        "levels": cmd_levels,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
