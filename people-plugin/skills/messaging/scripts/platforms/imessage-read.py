#!/usr/bin/env python3
"""
iMessage History Reader - Query chat.db for message history.

Read recent messages or search by keyword for a specific contact.
Requires Full Disk Access permission for Terminal to access ~/Library/Messages/chat.db.

Usage:
    # Get recent messages with a contact (by phone)
    python imessage-read.py --contact "+61418323408" --recent 10

    # Get recent messages (by name - resolves from contacts.yaml)
    python imessage-read.py --contact "James" --recent 10

    # Search messages by keyword
    python imessage-read.py --contact "James" --keyword "movie"

    # Messages since a specific date
    python imessage-read.py --contact "+61418323408" --since "2025-12-25"

    # Combine filters
    python imessage-read.py --contact "James" --keyword "meeting" --since "2025-12-01" --recent 20

Environment Variables:
    CLAUDE_PLUGIN_ROOT - Plugin root directory (for contacts.yaml resolution)
"""

import argparse
import os
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Try to import yaml, fall back to manual parsing if not available
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Constants
CHAT_DB = Path.home() / "Library" / "Messages" / "chat.db"
APPLE_EPOCH_OFFSET = 978307200  # Seconds between Unix epoch (1970) and Apple epoch (2001)


def extract_text_from_attributed_body(data: bytes) -> Optional[str]:
    """
    Extract plain text from NSAttributedString binary data.

    Modern macOS stores message content in attributedBody as NSKeyedArchiver data.
    The actual text is embedded within the binary - we extract it by finding
    the NSString content.
    """
    if not data:
        return None

    try:
        # The text is typically stored after a specific marker in the binary
        # Look for the text content between markers
        # NSAttributedString stores the string after "NSString" marker

        # Try to decode as UTF-8 and extract readable text
        # The format has the text after a length prefix

        # Method 1: Look for text after "NSString" or similar markers
        text_match = re.search(rb'NSString.{1,20}?([\x20-\x7e\xc0-\xff]{2,})', data)
        if text_match:
            try:
                return text_match.group(1).decode('utf-8', errors='ignore').strip()
            except:
                pass

        # Method 2: Find the longest readable string sequence
        # The actual message text is usually the longest readable segment
        readable_segments = re.findall(rb'[\x20-\x7e\xc0-\xff]{4,}', data)
        if readable_segments:
            # Filter out known metadata strings
            filtered = [
                s for s in readable_segments
                if not any(x in s.lower() for x in [b'nsstring', b'nsmutablestring', b'nsattributed', b'streamtyped'])
            ]
            if filtered:
                # Get the longest segment that looks like actual text
                longest = max(filtered, key=len)
                try:
                    decoded = longest.decode('utf-8', errors='ignore').strip()
                    if len(decoded) > 0:
                        return decoded
                except:
                    pass

        # Method 3: Try plistlib for proper decoding (if it's a valid bplist)
        if data.startswith(b'bplist'):
            try:
                import plistlib
                plist = plistlib.loads(data)
                # Navigate the structure to find the string
                if isinstance(plist, dict) and '$objects' in plist:
                    for obj in plist['$objects']:
                        if isinstance(obj, str) and len(obj) > 1 and obj not in ['$null', 'NSString', 'NSMutableString']:
                            return obj
            except:
                pass

    except Exception:
        pass

    return None


def check_fda_access() -> bool:
    """Check if we have Full Disk Access to chat.db."""
    if not CHAT_DB.exists():
        return False
    try:
        conn = sqlite3.connect(f"file:{CHAT_DB}?mode=ro", uri=True)
        conn.execute("SELECT 1 FROM message LIMIT 1")
        conn.close()
        return True
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        return False


def load_contacts(contacts_path: Optional[str] = None) -> dict:
    """
    Load contacts from YAML file.

    Returns dict mapping names/nicknames to platform identifiers.
    """
    if contacts_path is None:
        # Try to find contacts.yaml relative to this script
        plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT")
        if plugin_root:
            contacts_path = os.path.join(plugin_root, "skills", "messaging", "references", "contacts.yaml")
        else:
            # Fallback: relative to script location
            script_dir = Path(__file__).parent.parent.parent
            contacts_path = script_dir / "references" / "contacts.yaml"

    contacts_path = Path(contacts_path)
    if not contacts_path.exists():
        return {}

    if HAS_YAML:
        with open(contacts_path) as f:
            data = yaml.safe_load(f)
            return data.get("contacts", []) if data else []
    else:
        # Simple manual parsing for contacts
        # This is a fallback - yaml module is preferred
        return []


def resolve_contact(identifier: str, contacts: list) -> tuple[str, str]:
    """
    Resolve a contact name/nickname to phone number for iMessage.

    Returns (display_name, phone_or_email).
    If identifier looks like a phone/email, returns it directly.
    """
    # Check if identifier is already a phone number or email
    if identifier.startswith("+") or "@" in identifier:
        return (identifier, identifier)

    # Search contacts by name or nickname
    identifier_lower = identifier.lower()
    for contact in contacts:
        name = contact.get("name", "")
        nicknames = contact.get("nicknames", [])

        # Check name match
        if identifier_lower == name.lower():
            imessage_info = contact.get("platforms", {}).get("imessage", {})
            phone = imessage_info.get("phone") or imessage_info.get("email")
            if phone:
                return (name, phone)

        # Check nickname match
        for nick in nicknames:
            if identifier_lower == nick.lower():
                imessage_info = contact.get("platforms", {}).get("imessage", {})
                phone = imessage_info.get("phone") or imessage_info.get("email")
                if phone:
                    return (contact.get("name", nick), phone)

    # Not found - return as-is (might be a direct identifier)
    return (identifier, identifier)


def get_messages(
    contact_id: str,
    limit: int = 10,
    keyword: Optional[str] = None,
    since: Optional[str] = None
) -> list[dict]:
    """
    Query messages from chat.db for a specific contact.

    Args:
        contact_id: Phone number (e.g., +61418323408) or email
        limit: Maximum number of messages to return
        keyword: Optional keyword to filter messages
        since: Optional date string (YYYY-MM-DD) to filter messages after

    Returns:
        List of message dicts with keys: text, is_from_me, date, contact
    """
    conn = sqlite3.connect(f"file:{CHAT_DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    # Build query - include attributedBody for modern macOS message storage
    query = """
        SELECT
            m.text,
            m.attributedBody,
            m.is_from_me,
            datetime(m.date/1000000000 + ?, 'unixepoch', 'localtime') as formatted_date,
            m.date as raw_date,
            h.id as contact_id
        FROM message m
        LEFT JOIN handle h ON m.handle_id = h.ROWID
        WHERE h.id = ?
    """
    params = [APPLE_EPOCH_OFFSET, contact_id]

    # Add date filter
    if since:
        try:
            since_date = datetime.strptime(since, "%Y-%m-%d")
            # Convert to Apple epoch nanoseconds
            since_timestamp = (since_date.timestamp() - APPLE_EPOCH_OFFSET) * 1_000_000_000
            query += " AND m.date >= ?"
            params.append(since_timestamp)
        except ValueError:
            pass  # Invalid date format, ignore filter

    query += " ORDER BY m.date DESC LIMIT ?"
    params.append(limit * 2)  # Fetch extra to account for empty messages we'll filter

    cursor = conn.execute(query, params)
    messages = []

    for row in cursor:
        # Try text column first, fall back to attributedBody
        text = row["text"]
        if not text or text.strip() == '':
            # Try to extract from attributedBody (modern macOS format)
            attributed_body = row["attributedBody"]
            if attributed_body:
                text = extract_text_from_attributed_body(attributed_body)

        # Skip messages with no extractable text
        if not text or text.strip() == '':
            continue

        # Apply keyword filter (post-query since we extract from binary)
        if keyword and keyword.lower() not in text.lower():
            continue

        messages.append({
            "text": text,
            "is_from_me": bool(row["is_from_me"]),
            "date": row["formatted_date"],
            "contact": row["contact_id"]
        })

        # Stop once we have enough messages
        if len(messages) >= limit:
            break

    conn.close()
    return messages


def format_output(messages: list[dict], contact_name: str, contact_id: str) -> str:
    """Format messages as a conversational thread."""
    if not messages:
        return f"No messages found with {contact_name} ({contact_id})"

    lines = [
        f"Conversation with {contact_name} ({contact_id}) via iMessage",
        f"Showing {len(messages)} messages (most recent first):",
        ""
    ]

    for msg in messages:
        sender = "Me" if msg["is_from_me"] else contact_name
        # Format: [2025-12-26 21:38] Sender: Message text
        text = msg["text"].replace("\n", " ↵ ")  # Replace newlines for readability
        lines.append(f"[{msg['date']}] {sender}: {text}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read iMessage history for a contact",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s --contact "+61418323408" --recent 10
    %(prog)s --contact "James" --keyword "meeting"
    %(prog)s --contact "James" --since "2025-12-25"
        """
    )

    parser.add_argument(
        "--contact", "-c",
        required=True,
        help="Contact phone number, email, or name (resolved from contacts.yaml)"
    )
    parser.add_argument(
        "--recent", "-n",
        type=int,
        default=10,
        help="Number of recent messages to retrieve (default: 10)"
    )
    parser.add_argument(
        "--keyword", "-k",
        help="Filter messages containing this keyword"
    )
    parser.add_argument(
        "--since", "-s",
        help="Only show messages since this date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--contacts-file",
        help="Path to contacts.yaml (default: auto-detect from CLAUDE_PLUGIN_ROOT)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted text"
    )

    args = parser.parse_args()

    # Check Full Disk Access
    if not check_fda_access():
        print("ERROR: Cannot access iMessage database.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Grant Full Disk Access to your terminal app:", file=sys.stderr)
        print("  1. Open System Settings", file=sys.stderr)
        print("  2. Go to Privacy & Security > Full Disk Access", file=sys.stderr)
        print("  3. Click + and add your terminal (Terminal, iTerm, Warp, etc.)", file=sys.stderr)
        print("  4. Restart your terminal", file=sys.stderr)
        return 1

    # Load contacts and resolve identifier
    contacts = load_contacts(args.contacts_file)
    contact_name, contact_id = resolve_contact(args.contact, contacts)

    # Get messages
    messages = get_messages(
        contact_id=contact_id,
        limit=args.recent,
        keyword=args.keyword,
        since=args.since
    )

    # Output
    if args.json:
        import json
        output = {
            "contact_name": contact_name,
            "contact_id": contact_id,
            "message_count": len(messages),
            "messages": messages
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_output(messages, contact_name, contact_id))

    return 0


if __name__ == "__main__":
    sys.exit(main())
