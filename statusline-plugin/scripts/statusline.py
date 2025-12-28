#!/usr/bin/env python3
"""Claude Code Statusline - shows context with tokens, time, session/weekly usage."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# ANSI Colors
R = '\033[0m'
B = '\033[1m'
DIM = '\033[2m'
RED = '\033[31m'
GRN = '\033[32m'
YLW = '\033[33m'
BLU = '\033[34m'
MAG = '\033[35m'
CYN = '\033[36m'

USAGE_CACHE = Path('/tmp/claude_usage_api.cache')
USAGE_MAX_AGE = 60  # seconds
CREDS_FILE = Path.home() / '.config/claude-usage-widget/credentials.json'
CLIENT_ID = '9d1c250a-e61b-44d9-88ed-5944d1962f5e'


def get_claude_code_token() -> str | None:
    """Get token from Claude Code's credentials."""
    # Linux: Read from ~/.claude/.credentials.json
    linux_creds = Path.home() / '.claude' / '.credentials.json'
    if linux_creds.exists():
        try:
            data = json.loads(linux_creds.read_text())
            token = data.get('claudeAiOauth', {}).get('accessToken')
            if token:
                return token
        except Exception:
            pass

    # macOS: Try keychain
    try:
        result = subprocess.run(
            ['security', 'find-generic-password', '-s', 'Claude Code-credentials', '-w'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            raw = result.stdout.strip()
            # Keychain stores data as hex-encoded string
            try:
                decoded = bytes.fromhex(raw).decode('utf-8')
                # Extract claudeAiOauth JSON object using regex (structure is complex)
                match = re.search(r'"claudeAiOauth":(\{[^}]+\})', decoded)
                if match:
                    oauth_data = json.loads(match.group(1))
                    return oauth_data.get('accessToken')
            except (ValueError, UnicodeDecodeError):
                # Fallback: try parsing as raw JSON (older format)
                data = json.loads(raw)
                return data.get('claudeAiOauth', {}).get('accessToken')
    except Exception:
        pass
    return None


def refresh_token() -> str | None:
    """Refresh the OAuth token using the refresh token."""
    if not CREDS_FILE.exists():
        return None

    try:
        creds = json.loads(CREDS_FILE.read_text())
        refresh_tok = creds.get('accounts', [{}])[0].get('refreshToken')
        if not refresh_tok:
            return None

        import urllib.request
        import urllib.error

        data = json.dumps({
            'grant_type': 'refresh_token',
            'refresh_token': refresh_tok,
            'client_id': CLIENT_ID
        }).encode()

        req = urllib.request.Request(
            'https://console.anthropic.com/v1/oauth/token',
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())

        new_access = result.get('access_token')
        if not new_access:
            return None

        new_refresh = result.get('refresh_token', refresh_tok)
        expires_in = result.get('expires_in', 3600)
        expires_at = time.time() + expires_in

        # Update credentials file
        creds['accounts'][0]['accessToken'] = new_access
        creds['accounts'][0]['refreshToken'] = new_refresh
        creds['accounts'][0]['expiresAt'] = expires_at

        CREDS_FILE.write_text(json.dumps(creds, indent=2))
        os.chmod(CREDS_FILE, 0o600)

        return new_access
    except Exception:
        return None


def get_usage() -> tuple[int, int]:
    """Get 5-hour and 7-day usage percentages from Anthropic API."""
    now = time.time()

    # Check cache
    if USAGE_CACHE.exists():
        try:
            parts = USAGE_CACHE.read_text().strip().split()
            if len(parts) == 3:
                cache_time, five_hour, seven_day = float(parts[0]), int(parts[1]), int(parts[2])
                if now - cache_time < USAGE_MAX_AGE:
                    return five_hour, seven_day
        except (ValueError, IndexError):
            pass

    # Try Claude Code's keychain first (always fresh)
    token = get_claude_code_token()

    # Fall back to widget credentials if keychain fails
    if not token and CREDS_FILE.exists():
        try:
            creds = json.loads(CREDS_FILE.read_text())
            account = creds.get('accounts', [{}])[0]
            token = account.get('accessToken')
            expires_at = account.get('expiresAt', 0)

            # Refresh if expired (with 5 min buffer)
            if expires_at < now + 300:
                token = refresh_token()
        except Exception:
            pass

    if not token:
        return 0, 0

    try:
        import urllib.request
        import urllib.error

        req = urllib.request.Request(
            'https://api.anthropic.com/api/oauth/usage',
            headers={
                'Authorization': f'Bearer {token}',
                'anthropic-beta': 'oauth-2025-04-20',
                'User-Agent': 'claude-code/2.0.31',
                'Content-Type': 'application/json'
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError:
            # Try refresh and retry
            token = refresh_token()
            if token:
                req.add_header('Authorization', f'Bearer {token}')
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read())
            else:
                return 0, 0

        five_hour = round(data.get('five_hour', {}).get('utilization', 0))
        seven_day = round(data.get('seven_day', {}).get('utilization', 0))

        # Update cache
        USAGE_CACHE.write_text(f'{now} {five_hour} {seven_day}')

        return five_hour, seven_day
    except Exception:
        return 0, 0


def make_bar(pct: int, width: int = 8) -> str:
    """Create a progress bar. Uses ceiling for non-zero percentages so any usage shows."""
    if pct <= 0:
        filled = 0
    else:
        # Round up: any non-zero percentage shows at least 1 block
        filled = min(max((pct * width + 99) // 100, 1), width)
    return '■' * filled + '□' * (width - filled)


def bar_color(pct: int, red_threshold: int = 75) -> str:
    """Get color for progress bar based on percentage."""
    if pct < red_threshold // 2:
        return GRN
    elif pct < red_threshold:
        return YLW
    return RED


def format_duration(ms: int) -> str:
    """Format duration in milliseconds to human readable."""
    s = ms // 1000
    if s >= 3600:
        h = s // 3600
        m = (s % 3600) // 60
        return f'{h}h{m}m'
    elif s >= 60:
        return f'{s // 60}m'
    return f'{s}s'


def get_week_remaining() -> str:
    """Get days and hours remaining until end of week (Sunday midnight)."""
    now = datetime.now()

    # Calculate next Sunday midnight (start of Monday)
    days_until_sunday = (6 - now.weekday()) % 7
    if days_until_sunday == 0 and now.hour > 0:
        # If it's Sunday but not midnight yet, go to next Sunday
        days_until_sunday = 7

    next_sunday = now + timedelta(days=days_until_sunday)
    end_of_week = datetime(next_sunday.year, next_sunday.month, next_sunday.day, 0, 0, 0)

    # Calculate difference
    diff = end_of_week - now
    days = diff.days
    hours = diff.seconds // 3600

    # Format compact output
    if days > 0:
        result = f'{days}d{hours:02d}h'
    else:
        result = f'{hours}h'
    return result.rjust(5)


def get_session_remaining(session_pct: int) -> str:
    """Get time remaining in 5-hour session window."""
    # 5-hour window = 300 minutes
    total_minutes = 300
    remaining_pct = 100 - session_pct
    remaining_minutes = (remaining_pct * total_minutes) // 100

    hours = remaining_minutes // 60
    minutes = remaining_minutes % 60

    if hours > 0:
        result = f'{hours}h{minutes:02d}m'
    else:
        result = f'{minutes}m'
    return result.rjust(5)


def get_git_info(cwd: str) -> str:
    """Get git repo name, branch, and status."""
    try:
        # Check if in git repo
        subprocess.run(
            ['git', '-C', cwd, 'rev-parse', '--git-dir'],
            capture_output=True, check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not a git repo
        display_dir = cwd.replace(str(Path.home()), '~')
        return f'{BLU}{display_dir}{R}'

    try:
        # Get repo root and name
        result = subprocess.run(
            ['git', '-C', cwd, 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, check=True
        )
        repo_name = Path(result.stdout.strip()).name

        # Get branch
        result = subprocess.run(
            ['git', '-C', cwd, '--no-optional-locks', 'branch', '--show-current'],
            capture_output=True, text=True
        )
        branch = result.stdout.strip() or 'detached'

        # Get status
        status = ''

        # Unstaged changes
        result = subprocess.run(
            ['git', '-C', cwd, '--no-optional-locks', 'diff', '--quiet'],
            capture_output=True
        )
        if result.returncode != 0:
            status += '*'

        # Staged changes
        result = subprocess.run(
            ['git', '-C', cwd, '--no-optional-locks', 'diff', '--cached', '--quiet'],
            capture_output=True
        )
        if result.returncode != 0:
            status += '+'

        # Ahead/behind upstream
        result = subprocess.run(
            ['git', '-C', cwd, '--no-optional-locks', 'rev-parse', '--abbrev-ref', '@{u}'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            # Get ahead count
            result = subprocess.run(
                ['git', '-C', cwd, '--no-optional-locks', 'rev-list', '--count', '@{u}..HEAD'],
                capture_output=True, text=True
            )
            ahead = int(result.stdout.strip() or 0)
            if ahead > 0:
                status += f'+{ahead}'

            # Get behind count
            result = subprocess.run(
                ['git', '-C', cwd, '--no-optional-locks', 'rev-list', '--count', 'HEAD..@{u}'],
                capture_output=True, text=True
            )
            behind = int(result.stdout.strip() or 0)
            if behind > 0:
                status += f'-{behind}'

        # Format output
        if status:
            return f'{BLU}{repo_name}{R}:{YLW}{branch}{R}[{RED}{status}{R}]'
        return f'{BLU}{repo_name}{R}:{GRN}{branch}{R}[{GRN}ok{R}]'

    except Exception:
        return f'{BLU}{cwd}{R}'


def format_tokens(num: int) -> str:
    """Format token count to compact form."""
    if num >= 1_000_000:
        return f'{num / 1_000_000:.1f}M'
    elif num >= 1_000:
        return f'{num / 1_000:.0f}K'
    return str(num)


def get_context_time_remaining(ctx_pct: int, ctx_size: int) -> str:
    """
    Estimate time remaining in context window.
    Rough estimate: Opus 4.5 generates ~50-100 tokens per second on complex tasks.
    Assume average of 75 tokens/sec output, and typical 3:1 input:output ratio for remaining capacity.
    """
    remaining_tokens = ctx_size * (100 - ctx_pct) // 100
    # Assume 25% output tokens of remaining capacity
    estimated_output_tokens = remaining_tokens // 4
    # At ~75 tokens/sec
    estimated_seconds = estimated_output_tokens // 75

    if estimated_seconds >= 3600:
        hours = estimated_seconds // 3600
        minutes = (estimated_seconds % 3600) // 60
        return f'{hours}h{minutes}m'
    elif estimated_seconds >= 60:
        minutes = estimated_seconds // 60
        return f'{minutes}m'
    elif estimated_seconds > 0:
        return f'{estimated_seconds}s'
    return '0s'


def main():
    # Read input from stdin
    try:
        data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        print('Error parsing input')
        return

    # Parse statusline data
    cwd = data.get('workspace', {}).get('current_dir', '~')
    model = data.get('model', {}).get('display_name', '?')
    cost = data.get('cost', {}).get('total_cost_usd', 0)
    ctx_size = data.get('context_window', {}).get('context_window_size', 200000)
    current_usage = data.get('context_window', {}).get('current_usage') or {}

    # Calculate total context tokens (input + cache_creation + cache_read)
    input_tokens = current_usage.get('input_tokens', 0)
    cache_creation = current_usage.get('cache_creation_input_tokens', 0)
    cache_read = current_usage.get('cache_read_input_tokens', 0)
    output_tokens = current_usage.get('output_tokens', 0)

    total_ctx_tokens = input_tokens + cache_creation + cache_read

    dur_ms = data.get('cost', {}).get('total_duration_ms', 0)
    ver = data.get('version', '?')

    # Get usage from API
    five_hour_pct, seven_day_pct = get_usage()

    # Context usage (use total tokens, not just cache_read)
    ctx_pct = min(total_ctx_tokens * 100 // ctx_size, 100) if ctx_size > 0 else 0
    ctx_bar = make_bar(ctx_pct)
    ctx_clr = bar_color(ctx_pct, red_threshold=40)

    # Session usage (5-hour) - warn earlier since it's a shorter window
    session_bar = make_bar(five_hour_pct)
    session_clr = bar_color(five_hour_pct, red_threshold=80)

    # Weekly usage (7-day)
    weekly_bar = make_bar(seven_day_pct)
    weekly_clr = bar_color(seven_day_pct, red_threshold=80)

    # Format values
    cost_fmt = f'${cost:.2f}'
    dur_fmt = format_duration(dur_ms)
    repo_part = get_git_info(cwd)
    week_remaining = get_week_remaining()
    context_remaining = get_context_time_remaining(ctx_pct, ctx_size)
    session_remaining = get_session_remaining(five_hour_pct)

    # Current time (24-hour format)
    current_time = datetime.now().strftime('%H:%M')

    # Token counts
    ctx_tokens_fmt = format_tokens(total_ctx_tokens)
    output_tokens_fmt = format_tokens(output_tokens)

    # Token split by source
    # Note: Claude Code doesn't provide token attribution by source (MCP/agents/conversation)
    # in the JSON input. To implement this, we would need to parse the transcript file at
    # data['transcript_path'] and categorize messages by their source/role.
    # For now, showing total input vs output tokens.
    # TODO: Parse transcript to show MCP vs agent vs conversation token split
    token_detail = f'{ctx_tokens_fmt}in {output_tokens_fmt}out'

    # Databricks profile
    db_profile = os.environ.get('DATABRICKS_CONFIG_PROFILE', '')
    db_part = f' | {MAG}db:{db_profile}{R}' if db_profile else ''

    # Format context size
    ctx_size_fmt = format_tokens(ctx_size)

    # Output
    print(
        f'{B}{CYN}{model}{R} | '
        f'ctx {ctx_clr}{ctx_bar}{R} {ctx_pct}%-{ctx_tokens_fmt}/{ctx_size_fmt} | '
        f'5h {session_clr}{session_bar}{R} {five_hour_pct}%-{session_remaining.strip()} | '
        f'7d {weekly_clr}{weekly_bar}{R} {seven_day_pct}%-{week_remaining.strip()} | '
        f'{GRN}{cost_fmt}{R} | '
        f'{MAG}{dur_fmt}{R} | '
        f'{repo_part}{db_part} | '
        f'{DIM}v{ver}{R}',
        end=''
    )


if __name__ == '__main__':
    main()
