#!/bin/bash
# ensure-gh-cli.sh - Check for GitHub CLI and install if missing

set -e

# Check if gh is installed
if command -v gh &> /dev/null; then
    echo "GitHub CLI is installed: $(gh --version | head -1)"

    # Check authentication status
    if gh auth status &> /dev/null; then
        echo "GitHub CLI is authenticated"
        GITHUB_USER=$(gh auth status 2>&1 | grep "Logged in to github.com account" | awk '{print $NF}')
        echo "Logged in as: $GITHUB_USER"
        exit 0
    else
        echo "GitHub CLI is not authenticated"
        echo "Please run: gh auth login"
        exit 1
    fi
else
    echo "GitHub CLI is not installed"

    # Check for Homebrew on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            echo "Installing GitHub CLI via Homebrew..."
            brew install gh
            echo "GitHub CLI installed successfully"
            echo "Please run: gh auth login"
            exit 0
        else
            echo "Homebrew not found. Please install GitHub CLI manually:"
            echo "  brew install gh"
            echo "  or visit: https://cli.github.com/"
            exit 1
        fi
    # Linux
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "Please install GitHub CLI:"
        echo "  Ubuntu/Debian: sudo apt install gh"
        echo "  Fedora: sudo dnf install gh"
        echo "  or visit: https://cli.github.com/"
        exit 1
    else
        echo "Please install GitHub CLI from: https://cli.github.com/"
        exit 1
    fi
fi
