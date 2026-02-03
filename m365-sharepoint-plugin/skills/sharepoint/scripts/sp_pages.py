#!/usr/bin/env python3
"""SharePoint page operations.

Read and analyze SharePoint modern pages, extract editable content,
and generate PnP PowerShell commands for modifications.

Usage:
    sp_pages.py get <site_url> <page_name>         # Get page content
    sp_pages.py list <site_url>                    # List all pages
    sp_pages.py sections <site_url> <page_name>   # Get page sections/web parts
    sp_pages.py edit-text <site_url> <page_name> <instance_id> "<new_text>"
    sp_pages.py pnp-connect <site_url>            # Generate PnP connect command

Examples:
    sp_pages.py list https://contoso.sharepoint.com/sites/MySite
    sp_pages.py get https://contoso.sharepoint.com/sites/MySite Home.aspx
    sp_pages.py sections https://contoso.sharepoint.com/sites/MySite Home.aspx
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests

# Add _lib to path
sys.path.insert(0, str(Path(__file__).parent))
from _lib.auth import SharePointAuth


@dataclass
class WebPart:
    """Represents a web part on a page."""
    instance_id: str
    web_part_type: str
    title: str
    content: str
    section: int
    column: int
    order: int


@dataclass
class PageSection:
    """Represents a section on a page."""
    order: int
    layout: str  # OneColumn, TwoColumn, etc.
    web_parts: list[WebPart]


@dataclass
class Page:
    """Represents a SharePoint modern page."""
    name: str
    title: str
    url: str
    layout: str
    sections: list[PageSection]
    raw_content: dict


def parse_site_url(site_url: str) -> tuple[str, str]:
    """Extract tenant and site path from URL.

    Args:
        site_url: Full SharePoint site URL

    Returns:
        Tuple of (tenant, site_relative_path)
    """
    parsed = urlparse(site_url)
    host = parsed.netloc  # e.g., contoso.sharepoint.com
    tenant = host.split(".")[0]  # e.g., contoso
    site_path = parsed.path  # e.g., /sites/MySite

    return tenant, site_path


def get_auth(site_url: str) -> SharePointAuth:
    """Get auth for a site URL."""
    tenant, _ = parse_site_url(site_url)
    return SharePointAuth(tenant=tenant)


def list_pages(site_url: str) -> list[dict]:
    """List all pages in a site.

    Args:
        site_url: Full SharePoint site URL

    Returns:
        List of page info dicts
    """
    auth = get_auth(site_url)
    headers = auth.get_headers()

    # Get site pages library
    endpoint = f"{site_url}/_api/web/lists/getbytitle('Site Pages')/items"
    params = {
        "$select": "Id,Title,FileLeafRef,FileRef,Created,Modified,Author/Title",
        "$expand": "Author",
        "$orderby": "Modified desc"
    }

    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()

    results = response.json().get("d", {}).get("results", [])

    pages = []
    for item in results:
        pages.append({
            "id": item.get("Id"),
            "title": item.get("Title") or item.get("FileLeafRef", "").replace(".aspx", ""),
            "filename": item.get("FileLeafRef"),
            "url": item.get("FileRef"),
            "created": item.get("Created"),
            "modified": item.get("Modified"),
            "author": item.get("Author", {}).get("Title", "Unknown")
        })

    return pages


def get_page_content(site_url: str, page_name: str) -> dict:
    """Get raw page content including canvas content.

    Args:
        site_url: Full SharePoint site URL
        page_name: Page filename (e.g., "Home.aspx")

    Returns:
        Page content dict
    """
    auth = get_auth(site_url)
    headers = auth.get_headers()

    # Ensure .aspx extension
    if not page_name.endswith(".aspx"):
        page_name = f"{page_name}.aspx"

    # Get page item with canvas content
    endpoint = f"{site_url}/_api/web/lists/getbytitle('Site Pages')/items"
    params = {
        "$filter": f"FileLeafRef eq '{page_name}'",
        "$select": "Id,Title,FileLeafRef,CanvasContent1,LayoutWebpartsContent,PageLayoutType,BannerImageUrl"
    }

    response = requests.get(endpoint, headers=headers, params=params)
    response.raise_for_status()

    results = response.json().get("d", {}).get("results", [])
    if not results:
        raise ValueError(f"Page not found: {page_name}")

    return results[0]


def parse_canvas_content(canvas_json: str) -> list[dict]:
    """Parse the CanvasContent1 JSON into structured web parts.

    Args:
        canvas_json: Raw CanvasContent1 JSON string

    Returns:
        List of web part dicts with parsed content
    """
    if not canvas_json:
        return []

    try:
        canvas = json.loads(canvas_json)
    except json.JSONDecodeError:
        return []

    web_parts = []
    for item in canvas:
        wp = {
            "instance_id": item.get("id"),
            "web_part_type": item.get("webPartId") or item.get("controlType"),
            "position": item.get("position", {}),
            "section": item.get("position", {}).get("sectionIndex", 0),
            "column": item.get("position", {}).get("controlIndex", 0),
            "order": item.get("position", {}).get("zoneIndex", 0),
        }

        # Extract content based on type
        if item.get("controlType") == 4:  # Text web part
            inner = item.get("webPartData", {}).get("innerHTML", "")
            wp["web_part_type"] = "Text"
            wp["content"] = inner
            wp["plain_text"] = strip_html(inner)
        elif item.get("controlType") == 3:  # Web part
            data = item.get("webPartData", {})
            wp["title"] = data.get("title", "")
            wp["properties"] = data.get("properties", {})
            wp["content"] = json.dumps(data.get("properties", {}), indent=2)
        else:
            wp["raw"] = item

        web_parts.append(wp)

    return web_parts


def strip_html(html: str) -> str:
    """Strip HTML tags from string."""
    clean = re.sub(r'<[^>]+>', '', html)
    return clean.strip()


def get_page_sections(site_url: str, page_name: str) -> list[dict]:
    """Get structured page sections and web parts.

    Args:
        site_url: Full SharePoint site URL
        page_name: Page filename

    Returns:
        List of sections with web parts
    """
    page_content = get_page_content(site_url, page_name)
    canvas = page_content.get("CanvasContent1", "")

    web_parts = parse_canvas_content(canvas)

    # Group by section
    sections = {}
    for wp in web_parts:
        section_idx = wp.get("section", 0)
        if section_idx not in sections:
            sections[section_idx] = {
                "section": section_idx,
                "web_parts": []
            }
        sections[section_idx]["web_parts"].append(wp)

    return list(sections.values())


def generate_pnp_connect(site_url: str) -> str:
    """Generate PnP PowerShell connect command.

    Args:
        site_url: Full SharePoint site URL

    Returns:
        PowerShell command string
    """
    return f'''# Connect to SharePoint site with PnP PowerShell
# Install module first: Install-Module PnP.PowerShell -Scope CurrentUser

Connect-PnPOnline -Url "{site_url}" -Interactive'''


def generate_pnp_edit_text(site_url: str, page_name: str, instance_id: str, new_text: str) -> str:
    """Generate PnP PowerShell command to edit a text web part.

    Args:
        site_url: Full SharePoint site URL
        page_name: Page filename
        instance_id: Web part instance ID
        new_text: New HTML content for the text part

    Returns:
        PowerShell command string
    """
    if not page_name.endswith(".aspx"):
        page_name = f"{page_name}.aspx"

    # Escape quotes in the text
    escaped_text = new_text.replace('"', '`"')

    return f'''# Connect first
Connect-PnPOnline -Url "{site_url}" -Interactive

# Update the text web part
Set-PnPPageTextPart -Page "{page_name}" -InstanceId "{instance_id}" -Text "{escaped_text}"

# Publish the page
Set-PnPPage -Identity "{page_name}" -Publish'''


def generate_pnp_add_section(site_url: str, page_name: str, layout: str = "OneColumn", order: int = 1) -> str:
    """Generate PnP command to add a section."""
    if not page_name.endswith(".aspx"):
        page_name = f"{page_name}.aspx"

    return f'''# Add a new section to the page
Add-PnPPageSection -Page "{page_name}" -SectionTemplate {layout} -Order {order}'''


def generate_pnp_add_text(site_url: str, page_name: str, text: str, section: int = 1, column: int = 1) -> str:
    """Generate PnP command to add a text web part."""
    if not page_name.endswith(".aspx"):
        page_name = f"{page_name}.aspx"

    escaped_text = text.replace('"', '`"')

    return f'''# Add text web part
Add-PnPPageTextPart -Page "{page_name}" -Text "{escaped_text}" -Section {section} -Column {column}'''


def format_output(data, output_format: str = "json") -> str:
    """Format data for output."""
    if output_format == "json":
        return json.dumps(data, indent=2, default=str)
    elif output_format == "table":
        if isinstance(data, list) and data:
            # Simple table format
            if isinstance(data[0], dict):
                keys = list(data[0].keys())
                lines = [" | ".join(str(k)[:20] for k in keys)]
                lines.append("-" * len(lines[0]))
                for item in data:
                    lines.append(" | ".join(str(item.get(k, ""))[:20] for k in keys))
                return "\n".join(lines)
        return str(data)
    else:
        return str(data)


def main():
    parser = argparse.ArgumentParser(
        description="SharePoint page operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # List pages
    list_parser = subparsers.add_parser("list", help="List all pages in a site")
    list_parser.add_argument("site_url", help="SharePoint site URL")
    list_parser.add_argument("-o", "--output", choices=["json", "table"], default="table")

    # Get page
    get_parser = subparsers.add_parser("get", help="Get page content")
    get_parser.add_argument("site_url", help="SharePoint site URL")
    get_parser.add_argument("page_name", help="Page filename (e.g., Home.aspx)")
    get_parser.add_argument("-o", "--output", choices=["json", "table"], default="json")

    # Get sections
    sections_parser = subparsers.add_parser("sections", help="Get page sections and web parts")
    sections_parser.add_argument("site_url", help="SharePoint site URL")
    sections_parser.add_argument("page_name", help="Page filename")
    sections_parser.add_argument("-o", "--output", choices=["json", "table"], default="json")

    # Generate edit command
    edit_parser = subparsers.add_parser("edit-text", help="Generate PnP command to edit text")
    edit_parser.add_argument("site_url", help="SharePoint site URL")
    edit_parser.add_argument("page_name", help="Page filename")
    edit_parser.add_argument("instance_id", help="Text web part instance ID")
    edit_parser.add_argument("new_text", help="New text/HTML content")

    # PnP connect
    connect_parser = subparsers.add_parser("pnp-connect", help="Generate PnP connect command")
    connect_parser.add_argument("site_url", help="SharePoint site URL")

    # Add section
    add_section_parser = subparsers.add_parser("add-section", help="Generate PnP command to add section")
    add_section_parser.add_argument("site_url", help="SharePoint site URL")
    add_section_parser.add_argument("page_name", help="Page filename")
    add_section_parser.add_argument("--layout", default="OneColumn",
                                     choices=["OneColumn", "TwoColumn", "TwoColumnLeft", "TwoColumnRight", "ThreeColumn"])
    add_section_parser.add_argument("--order", type=int, default=1)

    # Add text
    add_text_parser = subparsers.add_parser("add-text", help="Generate PnP command to add text")
    add_text_parser.add_argument("site_url", help="SharePoint site URL")
    add_text_parser.add_argument("page_name", help="Page filename")
    add_text_parser.add_argument("text", help="Text/HTML content")
    add_text_parser.add_argument("--section", type=int, default=1)
    add_text_parser.add_argument("--column", type=int, default=1)

    args = parser.parse_args()

    try:
        if args.command == "list":
            pages = list_pages(args.site_url)
            print(format_output(pages, args.output))

        elif args.command == "get":
            content = get_page_content(args.site_url, args.page_name)
            print(format_output(content, args.output))

        elif args.command == "sections":
            sections = get_page_sections(args.site_url, args.page_name)
            print(format_output(sections, args.output))

        elif args.command == "edit-text":
            cmd = generate_pnp_edit_text(args.site_url, args.page_name, args.instance_id, args.new_text)
            print(cmd)

        elif args.command == "pnp-connect":
            cmd = generate_pnp_connect(args.site_url)
            print(cmd)

        elif args.command == "add-section":
            cmd = generate_pnp_add_section(args.site_url, args.page_name, args.layout, args.order)
            print(cmd)

        elif args.command == "add-text":
            cmd = generate_pnp_add_text(args.site_url, args.page_name, args.text, args.section, args.column)
            print(cmd)

        return 0

    except requests.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
