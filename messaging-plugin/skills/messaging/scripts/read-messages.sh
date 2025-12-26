#!/bin/bash
# Multi-platform message reader
# Usage: read-messages.sh --platform <platform> --contact "<id>" [--recent N] [--keyword "text"]
#
# Platforms:
#   imessage  - Reads from local chat.db (requires Full Disk Access)
#   teams     - Use browser automation (see references/browser-reading.md)
#   whatsapp  - Use browser automation (see references/browser-reading.md)
#   messenger - Use browser automation (see references/browser-reading.md)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse arguments
PLATFORM=""
CONTACT=""
RECENT=10
KEYWORD=""
SINCE=""
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --platform) PLATFORM="$2"; shift 2 ;;
        --contact) CONTACT="$2"; shift 2 ;;
        --recent) RECENT="$2"; shift 2 ;;
        --keyword) KEYWORD="$2"; shift 2 ;;
        --since) SINCE="$2"; shift 2 ;;
        --json) JSON_OUTPUT=true; shift ;;
        -h|--help)
            echo "Usage: read-messages.sh --platform <platform> --contact <id> [options]"
            echo ""
            echo "Platforms:"
            echo "  imessage   Read from local Messages database (requires FDA)"
            echo "  teams      Use browser automation (see browser-reading.md)"
            echo "  whatsapp   Use browser automation (see browser-reading.md)"
            echo "  messenger  Use browser automation (see browser-reading.md)"
            echo ""
            echo "Options:"
            echo "  --contact   Contact phone, email, or name"
            echo "  --recent    Number of recent messages (default: 10)"
            echo "  --keyword   Filter by keyword"
            echo "  --since     Messages since date (YYYY-MM-DD)"
            echo "  --json      Output as JSON"
            exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Validate required arguments
if [[ -z "$PLATFORM" ]]; then
    echo "Error: --platform is required"
    exit 1
fi

if [[ -z "$CONTACT" ]]; then
    echo "Error: --contact is required"
    exit 1
fi

# Route to platform-specific handler
case "$PLATFORM" in
    imessage)
        # Build Python command
        CMD="python3 $SCRIPT_DIR/platforms/imessage-read.py --contact \"$CONTACT\" --recent $RECENT"

        if [[ -n "$KEYWORD" ]]; then
            CMD="$CMD --keyword \"$KEYWORD\""
        fi

        if [[ -n "$SINCE" ]]; then
            CMD="$CMD --since \"$SINCE\""
        fi

        if [[ "$JSON_OUTPUT" == true ]]; then
            CMD="$CMD --json"
        fi

        eval "$CMD"
        ;;

    teams|whatsapp|messenger)
        echo "Platform '$PLATFORM' requires browser automation."
        echo ""
        echo "Use claude-in-chrome MCP tools to read messages:"
        echo "  1. tabs_context_mcp - Get browser context"
        echo "  2. navigate - Go to the platform's web URL"
        echo "  3. find - Locate the conversation"
        echo "  4. computer (scroll) - Load more history"
        echo "  5. get_page_text - Extract message content"
        echo ""
        echo "See references/browser-reading.md for detailed workflows."
        echo ""
        case "$PLATFORM" in
            teams) echo "URL: https://teams.microsoft.com" ;;
            whatsapp) echo "URL: https://web.whatsapp.com" ;;
            messenger) echo "URL: https://messenger.com" ;;
        esac
        ;;

    *)
        echo "Error: Unknown platform '$PLATFORM'"
        echo "Supported platforms: imessage, teams, whatsapp, messenger"
        exit 1
        ;;
esac
