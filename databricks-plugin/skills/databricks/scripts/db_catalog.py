#!/usr/bin/env python3
"""
db_catalog.py - Unity Catalog operations.

Usage:
    db_catalog.py catalogs [-p PROFILE]
    db_catalog.py schemas CATALOG [-p PROFILE]
    db_catalog.py tables CATALOG.SCHEMA [-p PROFILE]
    db_catalog.py describe CATALOG.SCHEMA.TABLE [-p PROFILE]
    db_catalog.py volumes CATALOG.SCHEMA [-p PROFILE]
    db_catalog.py grants SECURABLE_TYPE FULL_NAME [-p PROFILE]

Examples:
    db_catalog.py catalogs -p DEV
    db_catalog.py schemas main -p DEV
    db_catalog.py tables main.default -p DEV
    db_catalog.py describe main.default.my_table -p DEV
"""

import argparse
import sys
from pathlib import Path

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))

from _lib.config import get_workspace_client, get_default_profile
from _lib.auth import validate_profile
from _lib.output import format_output, print_error


def cmd_catalogs(args):
    """List all catalogs."""
    w = get_workspace_client(args.profile)

    catalogs = list(w.catalogs.list())

    if not catalogs:
        print("No catalogs found")
        return 0

    data = []
    for cat in catalogs:
        data.append({
            'name': cat.name,
            'comment': cat.comment or '',
            'owner': cat.owner or 'N/A',
            'created_at': str(cat.created_at) if cat.created_at else 'N/A',
        })

    print(format_output(data, args.output))
    return 0


def cmd_schemas(args):
    """List schemas in a catalog."""
    w = get_workspace_client(args.profile)

    try:
        schemas = list(w.schemas.list(catalog_name=args.catalog))

        if not schemas:
            print(f"No schemas in catalog '{args.catalog}'")
            return 0

        data = []
        for schema in schemas:
            data.append({
                'name': schema.name,
                'full_name': schema.full_name or f"{args.catalog}.{schema.name}",
                'comment': schema.comment or '',
                'owner': schema.owner or 'N/A',
            })

        print(format_output(data, args.output))
        return 0
    except Exception as e:
        print_error(f"Failed to list schemas: {e}")
        return 1


def cmd_tables(args):
    """List tables in a schema."""
    w = get_workspace_client(args.profile)

    # Parse catalog.schema
    parts = args.schema_path.split('.')
    if len(parts) != 2:
        print_error("Schema path must be in format: CATALOG.SCHEMA")
        return 1

    catalog_name, schema_name = parts

    try:
        tables = list(w.tables.list(
            catalog_name=catalog_name,
            schema_name=schema_name
        ))

        if not tables:
            print(f"No tables in '{args.schema_path}'")
            return 0

        data = []
        for table in tables:
            data.append({
                'name': table.name,
                'type': table.table_type.value if table.table_type else 'N/A',
                'format': table.data_source_format.value if table.data_source_format else 'N/A',
                'owner': table.owner or 'N/A',
            })

        print(format_output(data, args.output))
        return 0
    except Exception as e:
        print_error(f"Failed to list tables: {e}")
        return 1


def cmd_describe(args):
    """Describe a table (show columns and metadata)."""
    w = get_workspace_client(args.profile)

    # Parse catalog.schema.table
    parts = args.table_path.split('.')
    if len(parts) != 3:
        print_error("Table path must be in format: CATALOG.SCHEMA.TABLE")
        return 1

    full_name = args.table_path

    try:
        table = w.tables.get(full_name=full_name)

        if args.output == "json":
            # Convert to dict for JSON output
            import json
            print(json.dumps({
                'name': table.name,
                'full_name': table.full_name,
                'table_type': table.table_type.value if table.table_type else None,
                'data_source_format': table.data_source_format.value if table.data_source_format else None,
                'owner': table.owner,
                'comment': table.comment,
                'storage_location': table.storage_location,
                'columns': [
                    {
                        'name': col.name,
                        'type': col.type_text,
                        'nullable': col.nullable,
                        'comment': col.comment
                    }
                    for col in (table.columns or [])
                ]
            }, indent=2))
        else:
            # Human-readable output
            print(f"Table: {table.full_name}")
            print(f"Type: {table.table_type.value if table.table_type else 'N/A'}")
            print(f"Format: {table.data_source_format.value if table.data_source_format else 'N/A'}")
            print(f"Owner: {table.owner or 'N/A'}")
            print(f"Comment: {table.comment or 'N/A'}")
            print(f"Location: {table.storage_location or 'N/A'}")
            print()

            if table.columns:
                print("Columns:")
                col_data = []
                for col in table.columns:
                    col_data.append({
                        'name': col.name,
                        'type': col.type_text or 'N/A',
                        'nullable': 'Yes' if col.nullable else 'No',
                        'comment': col.comment or '',
                    })
                print(format_output(col_data, 'table'))

        return 0
    except Exception as e:
        print_error(f"Failed to describe table: {e}")
        return 1


def cmd_volumes(args):
    """List volumes in a schema."""
    w = get_workspace_client(args.profile)

    # Parse catalog.schema
    parts = args.schema_path.split('.')
    if len(parts) != 2:
        print_error("Schema path must be in format: CATALOG.SCHEMA")
        return 1

    catalog_name, schema_name = parts

    try:
        volumes = list(w.volumes.list(
            catalog_name=catalog_name,
            schema_name=schema_name
        ))

        if not volumes:
            print(f"No volumes in '{args.schema_path}'")
            return 0

        data = []
        for vol in volumes:
            data.append({
                'name': vol.name,
                'full_name': vol.full_name or f"{args.schema_path}.{vol.name}",
                'volume_type': vol.volume_type.value if vol.volume_type else 'N/A',
                'owner': vol.owner or 'N/A',
            })

        print(format_output(data, args.output))
        return 0
    except Exception as e:
        print_error(f"Failed to list volumes: {e}")
        return 1


def cmd_grants(args):
    """Show grants on a securable."""
    w = get_workspace_client(args.profile)

    # Map securable types
    securable_type = args.securable_type.upper()

    try:
        # The grants API varies by securable type
        from databricks.sdk.service.catalog import SecurableType

        type_map = {
            'CATALOG': SecurableType.CATALOG,
            'SCHEMA': SecurableType.SCHEMA,
            'TABLE': SecurableType.TABLE,
            'VOLUME': SecurableType.VOLUME,
            'FUNCTION': SecurableType.FUNCTION,
            'EXTERNAL_LOCATION': SecurableType.EXTERNAL_LOCATION,
            'STORAGE_CREDENTIAL': SecurableType.STORAGE_CREDENTIAL,
        }

        if securable_type not in type_map:
            print_error(f"Unknown securable type: {securable_type}")
            print(f"Valid types: {', '.join(type_map.keys())}")
            return 1

        grants = w.grants.get(
            securable_type=type_map[securable_type],
            full_name=args.full_name
        )

        if not grants.privilege_assignments:
            print(f"No grants on {securable_type} '{args.full_name}'")
            return 0

        data = []
        for assignment in grants.privilege_assignments:
            for priv in (assignment.privileges or []):
                data.append({
                    'principal': assignment.principal,
                    'privilege': priv.value if hasattr(priv, 'value') else str(priv),
                })

        print(format_output(data, args.output))
        return 0
    except Exception as e:
        print_error(f"Failed to get grants: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Unity Catalog operations"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Common arguments
    def add_common_args(p):
        p.add_argument("-p", "--profile", default=None, help="Databricks profile")
        p.add_argument("-o", "--output", choices=["table", "json", "csv"], default="table")

    # catalogs command
    catalogs_parser = subparsers.add_parser("catalogs", help="List catalogs")
    add_common_args(catalogs_parser)

    # schemas command
    schemas_parser = subparsers.add_parser("schemas", help="List schemas in a catalog")
    schemas_parser.add_argument("catalog", help="Catalog name")
    add_common_args(schemas_parser)

    # tables command
    tables_parser = subparsers.add_parser("tables", help="List tables in a schema")
    tables_parser.add_argument("schema_path", help="Schema path (CATALOG.SCHEMA)")
    add_common_args(tables_parser)

    # describe command
    describe_parser = subparsers.add_parser("describe", help="Describe a table")
    describe_parser.add_argument("table_path", help="Table path (CATALOG.SCHEMA.TABLE)")
    add_common_args(describe_parser)

    # volumes command
    volumes_parser = subparsers.add_parser("volumes", help="List volumes in a schema")
    volumes_parser.add_argument("schema_path", help="Schema path (CATALOG.SCHEMA)")
    add_common_args(volumes_parser)

    # grants command
    grants_parser = subparsers.add_parser("grants", help="Show grants on a securable")
    grants_parser.add_argument("securable_type", help="Type: CATALOG, SCHEMA, TABLE, VOLUME, etc.")
    grants_parser.add_argument("full_name", help="Full name of the securable")
    add_common_args(grants_parser)

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
        "catalogs": cmd_catalogs,
        "schemas": cmd_schemas,
        "tables": cmd_tables,
        "describe": cmd_describe,
        "volumes": cmd_volumes,
        "grants": cmd_grants,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
