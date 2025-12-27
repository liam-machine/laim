#!/bin/bash
# add-collaborator.sh - Add a GitHub user as a repository collaborator
#
# Usage:
#   add-collaborator.sh --repo "owner/repo" --user "username" [--permission push]
#
# Examples:
#   add-collaborator.sh --repo "liam-machine/my-project" --user "jamesdowzard"
#   add-collaborator.sh --repo "liam-machine/my-project" --user "jamesdowzard" --permission admin

set -e

# Parse arguments
REPO=""
USER=""
PERMISSION="push"  # Default to write access

while [[ $# -gt 0 ]]; do
    case $1 in
        --repo)
            REPO="$2"
            shift 2
            ;;
        --user)
            USER="$2"
            shift 2
            ;;
        --permission)
            PERMISSION="$2"
            shift 2
            ;;
        --help)
            echo "Usage: add-collaborator.sh --repo <owner/repo> --user <username> [--permission <level>]"
            echo ""
            echo "Options:"
            echo "  --repo        Repository in owner/repo format (required)"
            echo "  --user        GitHub username to add (required)"
            echo "  --permission  Permission level: pull, push (default), or admin"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$REPO" ]]; then
    echo "Error: --repo is required (format: owner/repo)"
    exit 1
fi

if [[ -z "$USER" ]]; then
    echo "Error: --user is required (GitHub username)"
    exit 1
fi

# Validate permission level
case $PERMISSION in
    pull|push|admin)
        ;;
    read)
        PERMISSION="pull"  # Normalize
        ;;
    write)
        PERMISSION="push"  # Normalize
        ;;
    *)
        echo "Error: Invalid permission level: $PERMISSION"
        echo "Valid options: pull (read), push (write), admin"
        exit 1
        ;;
esac

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    echo "Install with: brew install gh"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "Error: GitHub CLI is not authenticated. Run: gh auth login"
    exit 1
fi

# Add collaborator
echo "Adding $USER as collaborator to $REPO with $PERMISSION access..."

if gh api \
    --method PUT \
    -H "Accept: application/vnd.github+json" \
    "/repos/$REPO/collaborators/$USER" \
    -f permission="$PERMISSION" 2>/dev/null; then
    echo "Success: Invitation sent to $USER"
    echo "Permission level: $PERMISSION"
    echo "Note: $USER will receive an email to accept the invitation"
else
    # Check if user is already a collaborator
    if gh api "/repos/$REPO/collaborators/$USER" &>/dev/null; then
        echo "Note: $USER is already a collaborator on $REPO"
        echo "Updating permission level to: $PERMISSION"
        gh api \
            --method PUT \
            -H "Accept: application/vnd.github+json" \
            "/repos/$REPO/collaborators/$USER" \
            -f permission="$PERMISSION"
        echo "Success: Permission updated"
    else
        echo "Error: Failed to add collaborator. Check repository permissions."
        exit 1
    fi
fi
