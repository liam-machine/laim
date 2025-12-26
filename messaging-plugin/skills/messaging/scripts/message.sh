#!/bin/bash
# Multi-platform message sender
# Usage: message.sh --platform <platform> --recipient "<id>" --message "<msg>" [--send]
#
# Platforms: teams, whatsapp, imessage, messenger
# --send flag: Actually send (default is draft only)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
PLATFORM=""
RECIPIENT=""
MESSAGE=""
SEND_MODE="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --platform) PLATFORM="$2"; shift 2 ;;
        --recipient) RECIPIENT="$2"; shift 2 ;;
        --message) MESSAGE="$2"; shift 2 ;;
        --send) SEND_MODE="true"; shift ;;
        -h|--help)
            echo "Usage: message.sh --platform <platform> --recipient <id> --message <msg> [--send]"
            echo "Platforms: teams, whatsapp, imessage, messenger"
            echo ""
            echo "Options:"
            echo "  --platform   Platform to use (teams, whatsapp, imessage, messenger)"
            echo "  --recipient  Recipient identifier (email, phone, or username)"
            echo "  --message    Message content"
            echo "  --send       Send immediately instead of drafting"
            exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Validate required arguments
if [[ -z "$PLATFORM" ]]; then
    echo "Error: --platform is required"
    echo "Use: teams, whatsapp, imessage, or messenger"
    exit 1
fi

if [[ -z "$RECIPIENT" ]]; then
    echo "Error: --recipient is required"
    exit 1
fi

if [[ -z "$MESSAGE" ]]; then
    echo "Error: --message is required"
    exit 1
fi

# Route to platform-specific script
case "$PLATFORM" in
    teams)
        osascript "$SCRIPT_DIR/platforms/teams.scpt" "$RECIPIENT" "$MESSAGE" "$SEND_MODE"
        ;;
    whatsapp)
        bash "$SCRIPT_DIR/platforms/whatsapp.sh" "$RECIPIENT" "$MESSAGE" "$SEND_MODE"
        ;;
    imessage)
        osascript "$SCRIPT_DIR/platforms/imessage.scpt" "$RECIPIENT" "$MESSAGE" "$SEND_MODE"
        ;;
    messenger)
        bash "$SCRIPT_DIR/platforms/messenger.sh" "$RECIPIENT" "$MESSAGE" "$SEND_MODE"
        ;;
    *)
        echo "Error: Unknown platform '$PLATFORM'"
        echo "Supported platforms: teams, whatsapp, imessage, messenger"
        exit 1
        ;;
esac
