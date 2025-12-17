#!/bin/bash
# Teams Draft Message - Opens Teams chat and drafts a message
# Usage: teams-message.sh <recipient_email> <message>
#
# This script opens Microsoft Teams, navigates to a chat with the specified
# recipient, and drafts a message for the user to review and send.
#
# Requirements:
#   - macOS
#   - Microsoft Teams desktop app installed
#   - Accessibility permissions granted to Terminal
#
# Examples:
#   teams-message.sh john@company.com "Hello, how are you?"
#   teams-message.sh sarah@company.com "Meeting at 3pm?"

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    echo "Teams Draft Message"
    echo ""
    echo "Usage: teams-message.sh <recipient_email> <message>"
    echo ""
    echo "Arguments:"
    echo "  recipient_email  Email address of the Teams recipient"
    echo "  message          The message to draft"
    echo ""
    echo "Examples:"
    echo "  teams-message.sh john@company.com \"Hello, how are you?\""
    echo "  teams-message.sh sarah@company.com \"Meeting at 3pm?\""
    echo ""
    echo "Note: The message will be drafted but NOT sent automatically."
    echo "      You must review and click Send in Teams."
}

# Check for help flag
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    show_help
    exit 0
fi

# Validate arguments
if [ $# -lt 2 ]; then
    echo "Error: Missing required arguments"
    echo ""
    show_help
    exit 1
fi

RECIPIENT="$1"
MESSAGE="$2"

# Validate recipient email format (basic check)
if [[ ! "$RECIPIENT" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
    echo "Error: Invalid email format: $RECIPIENT"
    exit 1
fi

# Check if Teams is installed
if [ ! -d "/Applications/Microsoft Teams.app" ]; then
    echo "Error: Microsoft Teams is not installed"
    echo "Please install Microsoft Teams from the App Store or Microsoft website"
    exit 1
fi

# Run the AppleScript
osascript "$SCRIPT_DIR/teams_draft_message.scpt" "$RECIPIENT" "$MESSAGE"
