-- iMessage Draft/Send Script
-- Usage: osascript imessage.scpt <recipient> <message> <send_mode>
-- recipient: phone number or email
-- send_mode: "true" to send, "false" to draft only

on run argv
    if (count of argv) < 3 then
        error "Usage: osascript imessage.scpt <recipient> <message> <send_mode>"
    end if

    set recipientId to item 1 of argv
    set messageText to item 2 of argv
    set sendMode to item 3 of argv

    -- Validate inputs
    if recipientId is "" then
        error "Recipient cannot be empty"
    end if

    if messageText is "" then
        error "Message cannot be empty"
    end if

    tell application "Messages"
        activate
    end tell

    delay 1

    if sendMode is "true" then
        -- Send directly via Messages scripting
        tell application "Messages"
            try
                set targetService to 1st account whose service type = iMessage
                set targetBuddy to participant recipientId of targetService
                send messageText to targetBuddy
            on error errMsg
                -- Fallback: try sending to the buddy directly
                send messageText to buddy recipientId of (1st account whose service type = iMessage)
            end try
        end tell
        display notification "iMessage SENT to " & recipientId with title "iMessage Sent"
    else
        -- Draft only: Open compose window and type message
        tell application "System Events"
            tell process "Messages"
                set frontmost to true
                delay 0.5
                -- Cmd+N for new message
                keystroke "n" using command down
                delay 0.5
                -- Type recipient in the To field
                keystroke recipientId
                delay 0.3
                -- Tab to move to message field
                keystroke tab
                delay 0.3
                -- Type message
                keystroke messageText
            end tell
        end tell
        display notification "iMessage drafted for " & recipientId & ". Review and press Enter to send." with title "iMessage Draft Ready"
    end if

    return "Done"
end run
