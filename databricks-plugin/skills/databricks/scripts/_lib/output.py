"""
Output formatting utilities for Databricks plugin.

Provides consistent formatting across all scripts:
- Table format (default, human-readable)
- JSON format (programmatic use)
- CSV format (exports)
"""

import json
import sys
from typing import Any, List, Dict, Optional, Sequence


def format_output(
    data: Any,
    format: str = "table",
    columns: Optional[List[str]] = None
) -> str:
    """
    Format data for output.

    Args:
        data: Data to format (list of dicts, list of objects, or single item)
        format: Output format - 'table', 'json', or 'csv'
        columns: Optional list of columns to include (for table/csv)

    Returns:
        Formatted string
    """
    if format == "json":
        return format_json(data)
    elif format == "csv":
        return format_csv(data, columns)
    else:
        return format_table(data, columns)


def format_json(data: Any) -> str:
    """Format data as pretty-printed JSON."""
    # Handle SDK objects by converting to dict
    if hasattr(data, 'as_dict'):
        data = data.as_dict()
    elif isinstance(data, list):
        data = [
            item.as_dict() if hasattr(item, 'as_dict') else item
            for item in data
        ]

    return json.dumps(data, indent=2, default=str)


def format_csv(data: Any, columns: Optional[List[str]] = None) -> str:
    """Format data as CSV."""
    if not data:
        return ""

    # Normalize to list of dicts
    rows = _normalize_to_dicts(data)

    if not rows:
        return ""

    # Determine columns
    if columns is None:
        columns = list(rows[0].keys())

    lines = [",".join(columns)]

    for row in rows:
        values = []
        for col in columns:
            val = row.get(col, "")
            # Escape commas and quotes
            val_str = str(val) if val is not None else ""
            if "," in val_str or '"' in val_str:
                val_str = '"' + val_str.replace('"', '""') + '"'
            values.append(val_str)
        lines.append(",".join(values))

    return "\n".join(lines)


def format_table(data: Any, columns: Optional[List[str]] = None) -> str:
    """Format data as a markdown table."""
    if not data:
        return "No data"

    # Normalize to list of dicts
    rows = _normalize_to_dicts(data)

    if not rows:
        return "No data"

    # Determine columns
    if columns is None:
        columns = list(rows[0].keys())

    # Calculate column widths
    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            val = str(row.get(col, ""))[:50]  # Truncate long values
            widths[col] = max(widths[col], len(val))

    # Build table
    lines = []

    # Header
    header = "| " + " | ".join(col.ljust(widths[col]) for col in columns) + " |"
    lines.append(header)

    # Separator
    sep = "|" + "|".join("-" * (widths[col] + 2) for col in columns) + "|"
    lines.append(sep)

    # Rows
    for row in rows:
        values = []
        for col in columns:
            val = str(row.get(col, ""))[:50]
            values.append(val.ljust(widths[col]))
        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def _normalize_to_dicts(data: Any) -> List[Dict]:
    """Convert various data formats to list of dicts."""
    if isinstance(data, dict):
        return [data]

    if not isinstance(data, (list, tuple)):
        # Single object
        if hasattr(data, 'as_dict'):
            return [data.as_dict()]
        elif hasattr(data, '__dict__'):
            return [vars(data)]
        return [{"value": data}]

    # List of items
    result = []
    for item in data:
        if isinstance(item, dict):
            result.append(item)
        elif hasattr(item, 'as_dict'):
            result.append(item.as_dict())
        elif hasattr(item, '__dict__'):
            result.append(vars(item))
        else:
            result.append({"value": item})

    return result


def print_error(message: str) -> None:
    """Print error message to stderr."""
    print(f"Error: {message}", file=sys.stderr)


def print_success(message: str) -> None:
    """Print success message."""
    print(f"Success: {message}")


def print_warning(message: str) -> None:
    """Print warning message."""
    print(f"Warning: {message}")
