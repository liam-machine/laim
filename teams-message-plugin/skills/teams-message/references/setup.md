# Teams Message Skill Setup Guide

## Prerequisites

### 1. Microsoft Teams Desktop App

The Teams desktop app must be installed on your Mac. You can install it via:

**Homebrew:**
```bash
brew install --cask microsoft-teams
```

**Or download from:**
- [Microsoft Teams Download](https://www.microsoft.com/en-us/microsoft-teams/download-app)
- Mac App Store

### 2. Accessibility Permissions

This skill uses AppleScript to automate Teams, which requires Accessibility permissions.

**To grant permissions:**

1. Open **System Settings** (or System Preferences on older macOS)
2. Navigate to **Privacy & Security > Accessibility**
3. Click the lock icon and enter your password
4. Click the **+** button
5. Navigate to **Applications > Utilities > Terminal.app**
6. Add Terminal and ensure the toggle is **ON**

If you use a different terminal (iTerm2, Warp, etc.), add that application instead.

### 3. Sign into Teams

Ensure you're signed into Microsoft Teams with your work account before using this skill.

## Verification

Test the setup by running:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/teams-message/scripts/teams-message.sh --help
```

Then test with a real message:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/teams-message/scripts/teams-message.sh "colleague@company.com" "Test message"
```

## Troubleshooting

### Permission Denied Errors

If you see "osascript is not allowed to send keystrokes":
1. Re-check Accessibility permissions
2. Try removing and re-adding Terminal to the list
3. Restart Terminal after granting permissions

### Teams Not Opening Correct Chat

The deep link format requires the exact email address associated with the recipient's Microsoft account. Verify:
- The email is spelled correctly
- It matches their Teams/Microsoft account

### Message Not Appearing

If Teams opens but the message doesn't appear in the compose box:
1. Teams may need more time to load - the script waits 3 seconds by default
2. Edit `teams_draft_message.scpt` and increase the `delay 3` value to `delay 5`

### Teams Opens But Shows Error

Ensure:
- You're signed into Teams
- The recipient exists in your organization or is a known contact
- Your network allows Teams connections

## Script Locations

- **Shell script:** `${CLAUDE_PLUGIN_ROOT}/skills/teams-message/scripts/teams-message.sh`
- **AppleScript:** `${CLAUDE_PLUGIN_ROOT}/skills/teams-message/scripts/teams_draft_message.scpt`

## How the Scripts Work

1. **teams-message.sh** - Entry point that validates inputs and calls the AppleScript
2. **teams_draft_message.scpt** - AppleScript that:
   - Copies the message to clipboard
   - Opens Teams via `msteams://` deep link
   - Uses System Events to paste the message
   - Shows a notification when ready
