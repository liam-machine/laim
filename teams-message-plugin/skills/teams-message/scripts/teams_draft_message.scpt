-- Teams Draft Message Script
-- Opens a Teams chat and drafts a message for you to review and send
-- Usage: osascript teams_draft_message.scpt <recipient_email> <message>

on run argv
    -- Get parameters: recipient email and message
    if (count of argv) < 2 then
        log "Usage: osascript teams_draft_message.scpt <recipient_email> <message>"
        log "Example: osascript teams_draft_message.scpt john@company.com \"Hello, how are you?\""
        error "Missing required arguments: recipient_email and message"
    end if

    set recipientEmail to item 1 of argv
    set messageText to item 2 of argv

    -- Validate inputs
    if recipientEmail is "" then
        error "Recipient email cannot be empty"
    end if

    if messageText is "" then
        error "Message cannot be empty"
    end if

    -- Copy message to clipboard first
    set the clipboard to messageText

    -- Open Teams chat with the recipient using deep link
    set teamsURL to "msteams://teams.microsoft.com/l/chat/0/0?users=" & recipientEmail

    -- Activate Teams
    tell application "Microsoft Teams"
        activate
    end tell

    -- Open the chat URL
    do shell script "open " & quoted form of teamsURL

    -- Wait for Teams to open and load the chat
    delay 3

    -- Use System Events to paste the message from clipboard
    tell application "System Events"
        tell process "Microsoft Teams"
            set frontmost to true
            delay 0.5
            -- Paste from clipboard (Cmd+V)
            keystroke "v" using command down
        end tell
    end tell

    -- Notify user
    display notification "Message drafted in Teams. Review and click Send." with title "Teams Draft Ready"

    return "Draft created for " & recipientEmail
end run
