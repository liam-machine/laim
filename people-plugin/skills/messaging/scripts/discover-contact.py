#!/usr/bin/env python3
"""
Contact Discovery Script
Searches external sources (macOS Contacts) for contact information.
Used when a contact is not found in contacts.yaml.

Usage:
    python3 discover-contact.py --name "Charlotte Wynne"
    python3 discover-contact.py --name "John Smith" --include-messenger
"""

import argparse
import json
import subprocess
import sys
import re

def search_macos_contacts(name):
    """Search macOS Contacts app for a person by name."""
    # Escape single quotes in name for AppleScript
    escaped_name = name.replace("'", "'\\''")

    # First, get the contact name
    name_script = f'''
    tell application "Contacts"
        try
            set thePerson to first person whose name contains "{escaped_name}"
            return name of thePerson
        on error
            return "NOT_FOUND"
        end try
    end tell
    '''

    # Get phones
    phones_script = f'''
    tell application "Contacts"
        try
            set thePerson to first person whose name contains "{escaped_name}"
            return value of every phone of thePerson
        on error
            return {{}}
        end try
    end tell
    '''

    # Get emails
    emails_script = f'''
    tell application "Contacts"
        try
            set thePerson to first person whose name contains "{escaped_name}"
            return value of every email of thePerson
        on error
            return {{}}
        end try
    end tell
    '''

    try:
        # Get name
        name_result = subprocess.run(
            ['osascript', '-e', name_script],
            capture_output=True, text=True, timeout=10
        )
        full_name = name_result.stdout.strip()

        if full_name == "NOT_FOUND" or not full_name:
            return None

        # Get phones
        phones_result = subprocess.run(
            ['osascript', '-e', phones_script],
            capture_output=True, text=True, timeout=10
        )
        phones_raw = phones_result.stdout.strip()

        # Get emails
        emails_result = subprocess.run(
            ['osascript', '-e', emails_script],
            capture_output=True, text=True, timeout=10
        )
        emails_raw = emails_result.stdout.strip()

        # Parse phones - AppleScript returns comma-separated list
        phones = []
        if phones_raw:
            phones = [p.strip() for p in phones_raw.split(',') if p.strip()]

        # Parse emails - extract using regex since they might be concatenated
        emails = []
        if emails_raw:
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, emails_raw)

        # Normalize phone numbers (add + if missing for AU numbers)
        normalized_phones = []
        for phone in phones:
            phone = re.sub(r'[^\d+]', '', phone)  # Remove non-digits except +
            if phone.startswith('04') and len(phone) == 10:
                phone = '+61' + phone[1:]  # Convert 04xx to +614xx
            elif phone.startswith('614') and not phone.startswith('+'):
                phone = '+' + phone
            if phone:
                normalized_phones.append(phone)

        return {
            'name': full_name,
            'phones': normalized_phones,
            'emails': emails
        }

    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None

def format_discovery_result(macos_result, include_messenger_hint=False):
    """Format the discovery result as JSON."""
    if not macos_result:
        result = {
            'found': False,
            'source': None,
            'message': 'Contact not found in macOS Contacts'
        }
        if include_messenger_hint:
            result['messenger_hint'] = 'To find Messenger username, search Facebook friends list'
        return result

    result = {
        'found': True,
        'source': 'macos_contacts',
        'name': macos_result['name'],
        'phone': macos_result['phones'][0] if macos_result['phones'] else None,
        'all_phones': macos_result['phones'],
        'email': macos_result['emails'][0] if macos_result['emails'] else None,
        'all_emails': macos_result['emails']
    }

    if include_messenger_hint:
        result['messenger_hint'] = 'To find Messenger username, search Facebook friends list for this contact'

    return result

def main():
    parser = argparse.ArgumentParser(description='Discover contact information from external sources')
    parser.add_argument('--name', '-n', required=True, help='Name to search for')
    parser.add_argument('--include-messenger', '-m', action='store_true',
                        help='Include hint about finding Messenger username')
    args = parser.parse_args()

    # Search macOS Contacts
    macos_result = search_macos_contacts(args.name)

    # Format and output result
    result = format_discovery_result(macos_result, args.include_messenger)
    print(json.dumps(result, indent=2))

    sys.exit(0 if result['found'] else 1)

if __name__ == '__main__':
    main()
