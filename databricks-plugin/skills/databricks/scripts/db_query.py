#!/usr/bin/env python3
"""
db_query.py - Execute SQL queries on Databricks

Usage:
    db_query.py -c "SELECT * FROM table" [-p PROFILE] [-w WAREHOUSE] [-o FORMAT]
    db_query.py -f query.sql [-p PROFILE] [-w WAREHOUSE] [-o FORMAT]

Examples:
    db_query.py -c "SHOW DATABASES" -p DEV
    db_query.py -c "SELECT * FROM catalog.schema.table LIMIT 10" -p PROD -o csv
    db_query.py -f complex_query.sql -p DEV -o json
"""

import argparse
import sys
import time
from pathlib import Path

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))

from _lib.config import get_workspace_client, get_default_profile, get_profile_host
from _lib.auth import validate_profile
from _lib.output import format_output, format_table, print_error


def execute_query(
    query: str,
    profile: str,
    warehouse_id: str = None,
    timeout: str = "30s"
) -> dict:
    """
    Execute a SQL query on Databricks.

    Args:
        query: SQL query string
        profile: Profile name from ~/.databrickscfg
        warehouse_id: Optional warehouse ID override
        timeout: Wait timeout for query completion

    Returns:
        Dict with 'columns', 'data', 'row_count', 'status'
    """
    w = get_workspace_client(profile)

    # Get warehouse ID if not provided
    if not warehouse_id:
        # Try to get from environment or use first available
        warehouses = list(w.warehouses.list())
        running = [wh for wh in warehouses if wh.state and wh.state.value == "RUNNING"]

        if not running:
            raise ValueError(
                "No running SQL warehouses found. Start a warehouse or specify --warehouse"
            )
        warehouse_id = running[0].id

    # Execute query
    result = w.statement_execution.execute_statement(
        warehouse_id=warehouse_id,
        statement=query,
        wait_timeout=timeout
    )

    # Check status
    status = result.status
    if status.state.value == "FAILED":
        error = status.error
        raise RuntimeError(f"Query failed: {error.message if error else 'Unknown error'}")

    # Extract results
    manifest = result.manifest
    data = result.result

    columns = []
    if manifest and manifest.schema and manifest.schema.columns:
        columns = [col.name for col in manifest.schema.columns]

    rows = []
    if data and data.data_array:
        rows = data.data_array

    return {
        'columns': columns,
        'data': rows,
        'row_count': len(rows),
        'status': status.state.value
    }


def format_query_results(result: dict, format: str) -> str:
    """Format query results for display."""
    columns = result['columns']
    rows = result['data']

    if not rows:
        return f"Query returned 0 rows"

    # Convert to list of dicts
    data = []
    for row in rows:
        data.append(dict(zip(columns, row)))

    return format_output(data, format, columns)


def main():
    parser = argparse.ArgumentParser(
        description="Execute SQL queries on Databricks"
    )

    # Query source (mutually exclusive)
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument(
        "-c", "--command",
        help="SQL query to execute"
    )
    query_group.add_argument(
        "-f", "--file",
        help="File containing SQL query"
    )

    # Options
    parser.add_argument(
        "-p", "--profile",
        default=None,
        help="Databricks profile (default: from config or DEFAULT)"
    )
    parser.add_argument(
        "-w", "--warehouse",
        help="SQL warehouse ID (default: first running warehouse)"
    )
    parser.add_argument(
        "-o", "--output",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument(
        "-t", "--timeout",
        default="30s",
        help="Query timeout (default: 30s)"
    )

    args = parser.parse_args()

    # Get profile
    profile = args.profile or get_default_profile()

    # Validate profile
    is_valid, message = validate_profile(profile)
    if not is_valid:
        print_error(message)
        return 1

    # Get query
    if args.command:
        query = args.command
    else:
        try:
            with open(args.file, 'r') as f:
                query = f.read()
        except FileNotFoundError:
            print_error(f"Query file not found: {args.file}")
            return 1

    # Execute
    try:
        result = execute_query(
            query=query,
            profile=profile,
            warehouse_id=args.warehouse,
            timeout=args.timeout
        )

        output = format_query_results(result, args.output)
        print(output)

        if args.output == "table":
            print(f"\n{result['row_count']} row(s) returned")

        return 0

    except Exception as e:
        print_error(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
