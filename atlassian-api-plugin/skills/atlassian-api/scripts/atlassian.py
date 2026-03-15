#!/usr/bin/env python3
"""Thin Atlassian REST API client for Claude Code.

Usage:
    python atlassian.py METHOD PATH [--data JSON] [--params KEY=VAL ...] [--paginate]

Examples:
    python atlassian.py GET /rest/api/3/myself
    python atlassian.py POST /rest/api/3/search --data '{"jql":"project=EDP","maxResults":10}'
    python atlassian.py GET /wiki/api/v2/pages/123456 --params body-format=storage
    python atlassian.py GET /rest/api/3/search --params jql="project=EDP" maxResults=10
    python atlassian.py PUT /rest/api/3/issue/EDP-123 --data '{"fields":{"summary":"New title"}}'
    python atlassian.py GET /rest/api/3/issue/EDP-123/transitions
    python atlassian.py GET /wiki/rest/api/search --params cql='type=page AND space=EDP' --paginate

Credentials are read from ~/.atlassian-credentials (email, token, site).
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def load_credentials():
    """Read credentials from ~/.atlassian-credentials."""
    cred_path = os.path.expanduser("~/.atlassian-credentials")
    if not os.path.exists(cred_path):
        print("Error: ~/.atlassian-credentials not found.", file=sys.stderr)
        print("Create it with: email=..., token=..., site=...", file=sys.stderr)
        sys.exit(1)

    creds = {}
    with open(cred_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, val = line.split("=", 1)
                creds[key.strip()] = val.strip()

    for required in ("email", "token", "site"):
        if required not in creds:
            print(f"Error: '{required}' missing from ~/.atlassian-credentials", file=sys.stderr)
            sys.exit(1)

    return creds


def build_auth_header(email, token):
    """Build Basic auth header from email:token."""
    raw = f"{email}:{token}"
    encoded = base64.b64encode(raw.encode()).decode()
    return f"Basic {encoded}"


def make_request(method, url, headers, data=None, timeout=30):
    """Make HTTP request and return (status_code, response_body)."""
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode("utf-8")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return e.code, body
    except urllib.error.URLError as e:
        return 0, str(e.reason)


def parse_params(params_list):
    """Parse KEY=VAL pairs into a dict."""
    result = {}
    if not params_list:
        return result
    for p in params_list:
        if "=" in p:
            key, val = p.split("=", 1)
            result[key] = val
    return result


def format_output(status, body):
    """Pretty-print JSON response or show raw text."""
    if status == 0:
        print(f"Connection error: {body}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(body)
        # Truncate very large responses for readability
        output = json.dumps(data, indent=2, ensure_ascii=False)
        lines = output.split("\n")
        if len(lines) > 500:
            print("\n".join(lines[:500]))
            print(f"\n... (truncated, {len(lines)} total lines. Use --raw for full output)")
        else:
            print(output)
    except json.JSONDecodeError:
        print(body)

    if status >= 400:
        print(f"\nHTTP {status}", file=sys.stderr)
        sys.exit(1)


def paginate_request(method, base_url, headers, params, data=None, max_pages=5):
    """Follow pagination links and collect all results."""
    all_results = []
    page = 0
    url = base_url
    if params:
        url += "?" + urllib.parse.urlencode(params)

    while page < max_pages:
        status, body = make_request(method, url, headers, data)
        if status >= 400:
            format_output(status, body)
            return

        try:
            resp_data = json.loads(body)
        except json.JSONDecodeError:
            print(body)
            return

        # Jira-style pagination (startAt + total)
        if "issues" in resp_data:
            all_results.extend(resp_data["issues"])
            total = resp_data.get("total", 0)
            start_at = resp_data.get("startAt", 0)
            max_results = resp_data.get("maxResults", 50)
            if start_at + max_results >= total:
                break
            params["startAt"] = str(start_at + max_results)
            url = base_url + "?" + urllib.parse.urlencode(params)

        # Confluence v2 pagination (cursor in _links.next)
        elif "_links" in resp_data and "next" in resp_data.get("_links", {}):
            results_key = "results" if "results" in resp_data else None
            if results_key:
                all_results.extend(resp_data[results_key])
            next_path = resp_data["_links"]["next"]
            # next_path is relative, reconstruct full URL
            parsed = urllib.parse.urlparse(base_url)
            url = f"{parsed.scheme}://{parsed.netloc}{next_path}"
            params = {}  # params are in the next URL already

        # Confluence v1 pagination (start + limit + size)
        elif "results" in resp_data and "size" in resp_data:
            all_results.extend(resp_data["results"])
            size = resp_data.get("size", 0)
            limit = resp_data.get("limit", 25)
            if size < limit:
                break
            start = resp_data.get("start", 0)
            params["start"] = str(start + limit)
            url = base_url + "?" + urllib.parse.urlencode(params)

        else:
            # No pagination structure, just return as-is
            print(json.dumps(resp_data, indent=2, ensure_ascii=False))
            return

        page += 1

    # Print aggregated results
    print(json.dumps(all_results, indent=2, ensure_ascii=False))
    print(f"\n# Total: {len(all_results)} results across {page + 1} page(s)", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Atlassian REST API client for Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("method", choices=["GET", "POST", "PUT", "DELETE", "PATCH"],
                        help="HTTP method")
    parser.add_argument("path", help="API path (e.g. /rest/api/3/myself)")
    parser.add_argument("--data", "-d", help="JSON request body")
    parser.add_argument("--params", "-p", nargs="*", help="Query params as KEY=VAL pairs")
    parser.add_argument("--paginate", action="store_true",
                        help="Auto-paginate through all results (max 5 pages)")
    parser.add_argument("--max-pages", type=int, default=5,
                        help="Max pages when paginating (default: 5)")
    parser.add_argument("--raw", action="store_true",
                        help="Print full response without truncation")
    parser.add_argument("--timeout", type=int, default=30,
                        help="Request timeout in seconds (default: 30)")

    args = parser.parse_args()
    creds = load_credentials()

    # Build URL
    base_url = f"https://{creds['site']}{args.path}"
    params = parse_params(args.params)

    # Build headers
    headers = {
        "Authorization": build_auth_header(creds["email"], creds["token"]),
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Parse data
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            print(f"Error: --data is not valid JSON: {args.data}", file=sys.stderr)
            sys.exit(1)

    # Execute
    if args.paginate:
        paginate_request(args.method, base_url, headers, params, data, args.max_pages)
    else:
        if params:
            url = base_url + "?" + urllib.parse.urlencode(params)
        else:
            url = base_url

        status, body = make_request(args.method, url, headers, data, args.timeout)
        if args.raw:
            print(body)
        else:
            format_output(status, body)


if __name__ == "__main__":
    main()
