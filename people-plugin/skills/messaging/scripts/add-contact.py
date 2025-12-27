#!/usr/bin/env python3
"""
Add Contact Script
Appends a new contact to contacts.yaml with proper formatting.
Automatically adds discovered contacts after messaging someone new.

Usage:
    python3 add-contact.py --name "Jane Smith" --phone "+61400000000" --context personal
    python3 add-contact.py --name "Bob Jones" --phone "+61411111111" --email "bob@example.com" --messenger "bob.jones" --context personal --relationship "Friend"
"""

import argparse
import json
import os
import re
import sys

def get_contacts_path():
    """Get path to contacts.yaml, supporting CLAUDE_PLUGIN_ROOT."""
    plugin_root = os.environ.get('CLAUDE_PLUGIN_ROOT', '')
    if plugin_root:
        return os.path.join(plugin_root, 'skills', 'messaging', 'references', 'contacts.yaml')
    # Fallback to relative path from script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, '..', 'references', 'contacts.yaml')

def validate_phone(phone):
    """Validate phone number format (must start with +)."""
    if not phone:
        return None
    phone = phone.strip()
    if not phone.startswith('+'):
        # Try to normalize Australian numbers
        clean = re.sub(r'[^\d]', '', phone)
        if clean.startswith('04') and len(clean) == 10:
            phone = '+61' + clean[1:]
        elif clean.startswith('614') and len(clean) == 11:
            phone = '+' + clean
        else:
            return None  # Invalid format
    return phone

def validate_email(email):
    """Validate email format."""
    if not email:
        return None
    email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return email
    return None

def contact_exists(contacts_path, name):
    """Check if a contact with this name already exists."""
    try:
        with open(contacts_path, 'r') as f:
            content = f.read()
        # Check for exact name match
        pattern = rf'^\s+-\s+name:\s+{re.escape(name)}\s*$'
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            return True
        # Also check nicknames
        if re.search(rf'^\s+-\s+{re.escape(name)}\s*$', content, re.MULTILINE | re.IGNORECASE):
            return True
    except FileNotFoundError:
        pass
    return False

def generate_nicknames(name):
    """Generate sensible nicknames from full name."""
    parts = name.split()
    nicknames = []
    if len(parts) > 0:
        nicknames.append(parts[0])  # First name
    if len(parts) > 1:
        nicknames.append(parts[-1])  # Last name
    return nicknames

def format_contact_yaml(name, phone=None, email=None, messenger=None, context='personal', relationship=''):
    """Format a contact entry as YAML."""
    nicknames = generate_nicknames(name)

    lines = [
        f'  - name: {name}',
        '    nicknames:'
    ]
    for nick in nicknames:
        lines.append(f'      - {nick}')

    lines.append(f'    context: {context}')
    lines.append(f'    relationship: "{relationship}"')

    # Platforms
    lines.append('    platforms:')

    if phone:
        lines.append('      whatsapp:')
        lines.append(f'        phone: "{phone}"')
        lines.append('      imessage:')
        lines.append(f'        phone: "{phone}"')
        if email:
            lines.append(f'        email: "{email}"')

    if messenger:
        lines.append('      messenger:')
        lines.append(f'        username: "{messenger}"')

    # Default platform
    lines.append('    default_platform:')
    lines.append(f'      personal: {"imessage" if phone else "messenger"}')

    return '\n'.join(lines)

def add_contact(contacts_path, contact_yaml):
    """Add a contact to contacts.yaml before the template section."""
    try:
        with open(contacts_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        # Create new file with header
        content = '# Contacts Directory\n# This file is loaded when the messaging skill needs to resolve a contact.\n\ncontacts:\n'

    # Find insertion point (before the template comments)
    template_marker = '# ============================================================================'
    if template_marker in content:
        # Insert before the template section
        parts = content.split(template_marker, 1)
        new_content = parts[0].rstrip() + '\n\n' + contact_yaml + '\n\n' + template_marker + parts[1]
    else:
        # Append at end
        new_content = content.rstrip() + '\n\n' + contact_yaml + '\n'

    with open(contacts_path, 'w') as f:
        f.write(new_content)

def main():
    parser = argparse.ArgumentParser(description='Add a new contact to contacts.yaml')
    parser.add_argument('--name', '-n', required=True, help='Full name of the contact')
    parser.add_argument('--phone', '-p', help='Phone number (preferably with + country code)')
    parser.add_argument('--email', '-e', help='Email address')
    parser.add_argument('--messenger', '-m', help='Facebook Messenger username')
    parser.add_argument('--context', '-c', choices=['personal', 'work', 'personal_and_work'],
                        default='personal', help='Contact context (default: personal)')
    parser.add_argument('--relationship', '-r', default='', help='Relationship description')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Show what would be added without writing')

    args = parser.parse_args()

    contacts_path = get_contacts_path()

    # Check if contact already exists
    if contact_exists(contacts_path, args.name):
        result = {
            'success': False,
            'error': 'Contact already exists',
            'name': args.name
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Validate inputs
    phone = validate_phone(args.phone) if args.phone else None
    email = validate_email(args.email) if args.email else None

    if args.phone and not phone:
        result = {
            'success': False,
            'error': 'Invalid phone number format. Must start with + or be a valid AU mobile (04xx)',
            'provided': args.phone
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    if args.email and not email:
        result = {
            'success': False,
            'error': 'Invalid email format',
            'provided': args.email
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Must have at least one contact method
    if not phone and not email and not args.messenger:
        result = {
            'success': False,
            'error': 'Must provide at least one contact method (phone, email, or messenger)'
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Generate YAML
    contact_yaml = format_contact_yaml(
        name=args.name,
        phone=phone,
        email=email,
        messenger=args.messenger,
        context=args.context,
        relationship=args.relationship
    )

    if args.dry_run:
        result = {
            'success': True,
            'dry_run': True,
            'would_add': contact_yaml
        }
        print(json.dumps(result, indent=2))
        sys.exit(0)

    # Add to file
    add_contact(contacts_path, contact_yaml)

    result = {
        'success': True,
        'name': args.name,
        'phone': phone,
        'email': email,
        'messenger': args.messenger,
        'context': args.context,
        'file': contacts_path
    }
    print(json.dumps(result, indent=2))
    sys.exit(0)

if __name__ == '__main__':
    main()
