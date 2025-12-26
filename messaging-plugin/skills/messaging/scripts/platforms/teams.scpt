-- Teams Draft/Send Message Script
-- Usage: osascript teams.scpt <recipient_email> <message> <send_mode>
-- send_mode: "true" to send, "false" to draft only

on run argv
    if (count of argv) < 3 then
        error "Usage: osascript teams.scpt <recipient_email> <message> <send_mode>"
    end if

    set recipientEmail to item 1 of argv
    set messageText to item 2 of argv
    set sendMode to item 3 of argv

    -- Validate inputs
    if recipientEmail is "" then
        error "Recipient email cannot be empty"
    end if

    if messageText is "" then
        error "Message cannot be empty"
    end if

    -- Copy message to clipboard
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

            if sendMode is "true" then
                delay 0.3
                -- Press Enter to send
                keystroke return
                display notification "Message SENT to " & recipientEmail with title "Teams Message Sent"
            else
                display notification "Message drafted for " & recipientEmail & ". Review and click Send." with title "Teams Draft Ready"
            end if
        end tell
    end tell

    return "Done"
end run
