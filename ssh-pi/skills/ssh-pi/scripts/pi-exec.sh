#!/bin/bash
set -e

# pi-exec.sh - Execute commands and manage files on Raspberry Pi
# Usage: pi-exec.sh [--help] [--host HOST] COMMAND [ARGS...]
#
# Commands:
#   run "command"       Execute a command on Pi
#   script file.sh      Execute a local script on Pi
#   python file.py      Execute a local Python script on Pi
#   copy-to src dest    Copy file/dir to Pi
#   copy-from src dest  Copy file/dir from Pi
#   sync src dest       Rsync directory to Pi
#   sync-from src dest  Rsync directory from Pi
#   info                Show Pi system information
#   logs service        Show recent logs for a systemd service

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSH_HOST="${PI_SSH_HOST:-pi}"

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] COMMAND [ARGS...]

Execute commands and manage files on Raspberry Pi via SSH.

Options:
    -h, --help          Show this help message
    --host HOST         SSH host alias (default: pi, or \$PI_SSH_HOST)

Commands:
    run "command"       Execute a shell command on Pi
    script file.sh      Execute a local bash script on Pi
    python file.py      Execute a local Python script on Pi
    copy-to src dest    Copy file or directory to Pi
    copy-from src dest  Copy file or directory from Pi
    sync src dest       Rsync directory to Pi (incremental)
    sync-from src dest  Rsync directory from Pi
    info                Show Pi system information
    logs SERVICE [-f]   Show logs for systemd service (-f to follow)
    temp                Show CPU temperature
    disk                Show disk usage
    mem                 Show memory usage

Examples:
    $(basename "$0") run "ls -la /home/pi"
    $(basename "$0") script ./setup.sh
    $(basename "$0") python ./main.py
    $(basename "$0") sync ./project /home/pi/project
    $(basename "$0") logs nginx -f
EOF
}

check_ssh() {
    if ! ssh -o BatchMode=yes -o ConnectTimeout=5 "$SSH_HOST" exit 2>/dev/null; then
        echo "Error: Cannot connect to '$SSH_HOST'" >&2
        echo "Check SSH configuration or specify --host" >&2
        exit 1
    fi
}

cmd_run() {
    local command="$1"
    if [[ -z "$command" ]]; then
        echo "Error: No command specified" >&2
        echo "Usage: $(basename "$0") run \"command\"" >&2
        exit 1
    fi
    ssh "$SSH_HOST" "$command"
}

cmd_script() {
    local script_file="$1"
    if [[ ! -f "$script_file" ]]; then
        echo "Error: Script file not found: $script_file" >&2
        exit 1
    fi
    ssh "$SSH_HOST" 'bash -s' < "$script_file"
}

cmd_python() {
    local python_file="$1"
    shift
    local args="$*"
    if [[ ! -f "$python_file" ]]; then
        echo "Error: Python file not found: $python_file" >&2
        exit 1
    fi
    if [[ -n "$args" ]]; then
        # Copy file and run with args
        local remote_tmp="/tmp/$(basename "$python_file")"
        scp -q "$python_file" "$SSH_HOST:$remote_tmp"
        ssh "$SSH_HOST" "python3 '$remote_tmp' $args; rm -f '$remote_tmp'"
    else
        # Stream via stdin
        ssh "$SSH_HOST" 'python3' < "$python_file"
    fi
}

cmd_copy_to() {
    local src="$1"
    local dest="$2"
    if [[ -z "$src" || -z "$dest" ]]; then
        echo "Error: Source and destination required" >&2
        echo "Usage: $(basename "$0") copy-to src dest" >&2
        exit 1
    fi
    if [[ -d "$src" ]]; then
        scp -r "$src" "$SSH_HOST:$dest"
    else
        scp "$src" "$SSH_HOST:$dest"
    fi
    echo "Copied: $src -> $SSH_HOST:$dest"
}

cmd_copy_from() {
    local src="$1"
    local dest="$2"
    if [[ -z "$src" || -z "$dest" ]]; then
        echo "Error: Source and destination required" >&2
        echo "Usage: $(basename "$0") copy-from src dest" >&2
        exit 1
    fi
    scp -r "$SSH_HOST:$src" "$dest"
    echo "Copied: $SSH_HOST:$src -> $dest"
}

cmd_sync() {
    local src="$1"
    local dest="$2"
    if [[ -z "$src" || -z "$dest" ]]; then
        echo "Error: Source and destination required" >&2
        echo "Usage: $(basename "$0") sync src dest" >&2
        exit 1
    fi
    # Ensure trailing slash for directory sync
    [[ "$src" != */ ]] && src="${src}/"
    rsync -avz --progress \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='.venv' \
        --exclude='*.pyc' \
        "$src" "$SSH_HOST:$dest"
}

cmd_sync_from() {
    local src="$1"
    local dest="$2"
    if [[ -z "$src" || -z "$dest" ]]; then
        echo "Error: Source and destination required" >&2
        echo "Usage: $(basename "$0") sync-from src dest" >&2
        exit 1
    fi
    rsync -avz --progress "$SSH_HOST:$src" "$dest"
}

cmd_info() {
    ssh "$SSH_HOST" 'bash -s' << 'EOF'
echo "=== Raspberry Pi System Info ==="
echo ""
echo "Hostname: $(hostname)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
echo ""
echo "CPU Temperature: $(vcgencmd measure_temp 2>/dev/null | cut -d'=' -f2 || echo 'N/A')"
echo ""
echo "Memory:"
free -h | head -2
echo ""
echo "Disk:"
df -h / | tail -1 | awk '{print "  Used: " $3 " / " $2 " (" $5 " used)"}'
echo ""
echo "Uptime: $(uptime -p)"
echo "IP Addresses: $(hostname -I)"
EOF
}

cmd_logs() {
    local service="$1"
    local follow="$2"
    if [[ -z "$service" ]]; then
        echo "Error: Service name required" >&2
        echo "Usage: $(basename "$0") logs SERVICE [-f]" >&2
        exit 1
    fi
    if [[ "$follow" == "-f" ]]; then
        ssh "$SSH_HOST" "sudo journalctl -u '$service' -f"
    else
        ssh "$SSH_HOST" "sudo journalctl -u '$service' -n 50 --no-pager"
    fi
}

cmd_temp() {
    ssh "$SSH_HOST" "vcgencmd measure_temp"
}

cmd_disk() {
    ssh "$SSH_HOST" "df -h"
}

cmd_mem() {
    ssh "$SSH_HOST" "free -h"
}

# Parse options
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        --host)
            SSH_HOST="$2"
            shift 2
            ;;
        -*)
            echo "Unknown option: $1" >&2
            usage
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# Get command
COMMAND="${1:-}"
shift || true

if [[ -z "$COMMAND" ]]; then
    usage
    exit 1
fi

# Verify SSH connection (except for help)
check_ssh

# Execute command
case "$COMMAND" in
    run)        cmd_run "$@" ;;
    script)     cmd_script "$@" ;;
    python)     cmd_python "$@" ;;
    copy-to)    cmd_copy_to "$@" ;;
    copy-from)  cmd_copy_from "$@" ;;
    sync)       cmd_sync "$@" ;;
    sync-from)  cmd_sync_from "$@" ;;
    info)       cmd_info ;;
    logs)       cmd_logs "$@" ;;
    temp)       cmd_temp ;;
    disk)       cmd_disk ;;
    mem)        cmd_mem ;;
    *)
        echo "Unknown command: $COMMAND" >&2
        usage
        exit 1
        ;;
esac
