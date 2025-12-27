#!/bin/bash
# Facebook Messenger via deep link
# Usage: messenger.sh <username> <message> <send_mode>
# username: Facebook username for m.me/ link
# send_mode: "true" for send (not supported), "false" for draft

USERNAME="$1"
MESSAGE="$2"
SEND_MODE="$3"

if [[ -z "$USERNAME" || -z "$MESSAGE" ]]; then
    echo "Error: username and message required"
    echo "Usage: messenger.sh <username> <message> <send_mode>"
    exit 1
fi

# Copy message to clipboard since m.me doesn't support pre-filled text
echo -n "$MESSAGE" | pbcopy

# Open Messenger with the user
URL="https://m.me/${USERNAME}"

open "$URL"

if [[ "$SEND_MODE" == "true" ]]; then
    echo "Note: Messenger does not support auto-send via deep links."
    echo "Message copied to clipboard. Paste with Cmd+V and send manually."
fi

osascript -e 'display notification "Messenger opened. Message copied to clipboard - paste with Cmd+V." with title "Messenger Ready"'

echo "Done"
