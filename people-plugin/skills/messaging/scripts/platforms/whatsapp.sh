#!/bin/bash
# WhatsApp message via deep link
# Usage: whatsapp.sh <phone> <message> <send_mode>
# phone: International format with + (e.g., +61412345678)
# send_mode: "true" for send (not fully supported), "false" for draft

PHONE="$1"
MESSAGE="$2"
SEND_MODE="$3"

if [[ -z "$PHONE" || -z "$MESSAGE" ]]; then
    echo "Error: phone and message required"
    echo "Usage: whatsapp.sh <phone> <message> <send_mode>"
    exit 1
fi

# Remove + from phone for wa.me format
PHONE_CLEAN="${PHONE//+/}"
# Also remove any spaces or dashes
PHONE_CLEAN="${PHONE_CLEAN// /}"
PHONE_CLEAN="${PHONE_CLEAN//-/}"

# URL encode the message using Python
MESSAGE_ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$MESSAGE'''))")

# Open WhatsApp Web with the message pre-filled
URL="https://wa.me/${PHONE_CLEAN}?text=${MESSAGE_ENCODED}"

open "$URL"

if [[ "$SEND_MODE" == "true" ]]; then
    echo "Note: WhatsApp does not support auto-send via deep links."
    echo "Message drafted in browser/app. Please click Send manually."
    osascript -e 'display notification "WhatsApp opened with message. Click Send in the browser." with title "WhatsApp Ready"'
else
    osascript -e 'display notification "WhatsApp opened with message drafted. Review and click Send." with title "WhatsApp Draft Ready"'
fi

echo "Done"
