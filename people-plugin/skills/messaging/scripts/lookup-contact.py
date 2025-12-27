#!/usr/bin/env python3
"""
Contact Lookup Script
Searches contacts.yaml and returns only the matching contact as JSON.
Avoids loading full contact list into LLM context.

Usage:
    python3 lookup-contact.py --name "James"
    python3 lookup-contact.py --name "JD"  # searches nicknames too
"""

import argparse
import json
import os
import sys
import re

def get_contacts_path():
    """Get path to contacts.yaml, supporting CLAUDE_PLUGIN_ROOT."""
    plugin_root = os.environ.get('CLAUDE_PLUGIN_ROOT', '')
    if plugin_root:
        return os.path.join(plugin_root, 'skills', 'messaging', 'references', 'contacts.yaml')
    # Fallback to relative path from script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, '..', 'references', 'contacts.yaml')

def parse_yaml_contacts(filepath):
    """Parse contacts.yaml without external dependencies."""
    contacts = []
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        return contacts

    # Split by contact entries (- name:)
    contact_blocks = re.split(r'\n  - name:', content)

    for i, block in enumerate(contact_blocks[1:], 1):  # Skip header
        block = '  - name:' + block if i > 0 else block
        contact = parse_contact_block(block)
        if contact:
            contacts.append(contact)

    return contacts

def parse_contact_block(block):
    """Parse a single contact block into a dict."""
    contact = {}

    # Extract name
    name_match = re.search(r'name:\s*(.+)', block)
    if name_match:
        contact['name'] = name_match.group(1).strip()

    # Extract nicknames
    nicknames = []
    nickname_section = re.search(r'nicknames:\s*\n((?:\s+-\s+.+\n?)+)', block)
    if nickname_section:
        nicknames = re.findall(r'-\s+(.+)', nickname_section.group(1))
    contact['nicknames'] = [n.strip() for n in nicknames]

    # Extract context
    context_match = re.search(r'context:\s*(.+)', block)
    if context_match:
        contact['context'] = context_match.group(1).strip()

    # Extract relationship
    rel_match = re.search(r'relationship:\s*["\']?([^"\'\n]+)["\']?', block)
    if rel_match:
        contact['relationship'] = rel_match.group(1).strip()

    # Extract github handle
    github_match = re.search(r'github:\s*(\S+)', block)
    if github_match:
        contact['github'] = github_match.group(1).strip()

    # Extract work_keywords
    work_keywords = []
    wk_section = re.search(r'work_keywords:\s*\n((?:\s+#[^\n]*\n)*(?:\s+-\s+.+\n?)+)', block)
    if wk_section:
        work_keywords = re.findall(r'-\s+(.+)', wk_section.group(1))
    contact['work_keywords'] = [w.strip() for w in work_keywords]

    # Extract platforms
    platforms = {}

    # Teams
    teams_email = re.search(r'teams:\s*\n\s+email:\s*(.+)', block)
    if teams_email:
        platforms['teams'] = {'email': teams_email.group(1).strip()}

    # WhatsApp
    wa_phone = re.search(r'whatsapp:\s*\n\s+phone:\s*["\']?([^"\'\n]+)["\']?', block)
    if wa_phone:
        platforms['whatsapp'] = {'phone': wa_phone.group(1).strip()}

    # iMessage
    im_section = re.search(r'imessage:\s*\n((?:\s+\w+:\s*.+\n?)+)', block)
    if im_section:
        platforms['imessage'] = {}
        im_phone = re.search(r'phone:\s*["\']?([^"\'\n]+)["\']?', im_section.group(1))
        im_email = re.search(r'email:\s*["\']?([^"\'\n]+)["\']?', im_section.group(1))
        if im_phone:
            platforms['imessage']['phone'] = im_phone.group(1).strip()
        if im_email:
            platforms['imessage']['email'] = im_email.group(1).strip()

    # Messenger
    msg_username = re.search(r'messenger:\s*\n\s+username:\s*["\']?([^"\'\n#]+)["\']?', block)
    if msg_username:
        platforms['messenger'] = {'username': msg_username.group(1).strip()}

    contact['platforms'] = platforms

    # Extract default_platform
    default_platform = {}
    dp_section = re.search(r'default_platform:\s*\n((?:\s+\w+:\s*.+\n?)+)', block)
    if dp_section:
        work_default = re.search(r'work:\s*(\w+)', dp_section.group(1))
        personal_default = re.search(r'personal:\s*(\w+)', dp_section.group(1))
        if work_default:
            default_platform['work'] = work_default.group(1).strip()
        if personal_default:
            default_platform['personal'] = personal_default.group(1).strip()
    contact['default_platform'] = default_platform

    return contact if contact.get('name') else None

def find_contact(contacts, search_name):
    """Find a contact by name or nickname (case-insensitive)."""
    search_lower = search_name.lower()

    for contact in contacts:
        # Check main name
        if contact.get('name', '').lower() == search_lower:
            return contact

        # Check nicknames
        for nickname in contact.get('nicknames', []):
            if nickname.lower() == search_lower:
                return contact

    # Partial match fallback
    for contact in contacts:
        if search_lower in contact.get('name', '').lower():
            return contact
        for nickname in contact.get('nicknames', []):
            if search_lower in nickname.lower():
                return contact

    return None

def main():
    parser = argparse.ArgumentParser(description='Look up a contact by name or nickname')
    parser.add_argument('--name', '-n', required=True, help='Name or nickname to search for')
    args = parser.parse_args()

    contacts_path = get_contacts_path()
    contacts = parse_yaml_contacts(contacts_path)

    contact = find_contact(contacts, args.name)

    if contact:
        result = {
            'found': True,
            'name': contact.get('name'),
            'nicknames': contact.get('nicknames', []),
            'context': contact.get('context', 'personal'),
            'relationship': contact.get('relationship', ''),
            'github': contact.get('github'),
            'work_keywords': contact.get('work_keywords', []),
            'platforms': contact.get('platforms', {}),
            'default_platform': contact.get('default_platform', {})
        }
    else:
        result = {
            'found': False,
            'searched_for': args.name
        }

    print(json.dumps(result, indent=2))
    sys.exit(0 if contact else 1)

if __name__ == '__main__':
    main()
