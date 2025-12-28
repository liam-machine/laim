---
name: ssh-pi
description: Execute commands and develop on a Raspberry Pi via SSH. Use this skill when the user asks to "run on pi", "execute on raspberry pi", "ssh pi", "run this on the pi", "test on pi", "raspberry pi command", "deploy to pi", "check the pi", "install on pi", "run on the raspberry pi", or any request to execute code, scripts, or commands remotely on a Raspberry Pi. Also triggers for file operations like "copy to pi", "sync to pi", "deploy files to pi", or "get file from pi".
---

# SSH Pi - Raspberry Pi Remote Development

Execute commands, run scripts, and manage files on a Raspberry Pi via SSH for local Mac + remote Pi development workflows.

## Quick Reference

| Operation | Command |
|-----------|---------|
| Run command | `ssh pi "command"` |
| Run script | `ssh pi 'bash -s' < script.sh` |
| Copy to Pi | `scp local_file pi:remote_path` |
| Copy from Pi | `scp pi:remote_file local_path` |
| Sync directory | `rsync -avz --progress local_dir/ pi:remote_dir/` |
| System info | `${CLAUDE_PLUGIN_ROOT}/skills/ssh-pi/scripts/pi-exec.sh info` |

## Command Execution

### Single Commands

```bash
ssh pi "ls -la /home/pi"
ssh pi "python3 --version"
ssh pi "sudo systemctl status nginx"
```

### Commands with Special Characters

**Always use single quotes for the outer wrapper when the command contains:**
- Variables you want evaluated on Pi: `ssh pi 'echo $HOME'`
- Double quotes: `ssh pi 'grep "pattern" file.txt'`
- Pipes: `ssh pi 'ps aux | grep python'`

**Use double quotes when you need Mac-side variable expansion:**
```bash
LOCAL_VAR="myvalue"
ssh pi "echo ${LOCAL_VAR}"  # Expands on Mac before sending
```

### Multi-line Scripts

**Option 1: Heredoc (preferred for complex scripts)**
```bash
ssh pi 'bash -s' << 'EOF'
#!/bin/bash
echo "Running on Pi"
cd /home/pi/project
python3 -c "print('Hello from Pi')"
EOF
```

**Option 2: Pass local script via stdin**
```bash
ssh pi 'bash -s' < local_script.sh
```

**Option 3: Copy and execute**
```bash
scp script.sh pi:/tmp/ && ssh pi "chmod +x /tmp/script.sh && /tmp/script.sh"
```

### Python Execution on Pi

```bash
# Run Python one-liner
ssh pi "python3 -c 'print(1+1)'"

# Run Python script from stdin
ssh pi 'python3' << 'EOF'
import sys
print(f"Python {sys.version}")
print("Hello from Raspberry Pi!")
EOF

# Execute local Python file on Pi
ssh pi 'python3' < local_script.py
```

## Helper Script

Use the bundled helper for common operations:

```bash
# System info
${CLAUDE_PLUGIN_ROOT}/skills/ssh-pi/scripts/pi-exec.sh info

# Sync project directory
${CLAUDE_PLUGIN_ROOT}/skills/ssh-pi/scripts/pi-exec.sh sync ./project /home/pi/project

# Run local Python file on Pi
${CLAUDE_PLUGIN_ROOT}/skills/ssh-pi/scripts/pi-exec.sh python ./main.py

# View service logs
${CLAUDE_PLUGIN_ROOT}/skills/ssh-pi/scripts/pi-exec.sh logs nginx -f
```

## File Operations

### Copy Files

```bash
# Single file to Pi
scp myfile.txt pi:/home/pi/

# Single file from Pi
scp pi:/home/pi/results.json ./

# Directory to Pi (recursive)
scp -r ./my_project pi:/home/pi/projects/

# Directory from Pi
scp -r pi:/home/pi/data ./local_data
```

### Sync Directories (rsync)

**Preferred for development - only transfers changes:**

```bash
# Sync local project to Pi
rsync -avz --progress ./project/ pi:/home/pi/project/

# Sync with delete (mirror exactly)
rsync -avz --delete ./project/ pi:/home/pi/project/

# Exclude files (node_modules, .git, __pycache__)
rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
  ./project/ pi:/home/pi/project/

# Sync from Pi to Mac
rsync -avz pi:/home/pi/project/output/ ./output/
```

## Development Workflow

### Typical Workflow Pattern

1. **Develop locally** on Mac with Claude Code
2. **Sync code** to Pi: `rsync -avz ./project/ pi:/home/pi/project/`
3. **Run on Pi**: `ssh pi "cd /home/pi/project && python3 main.py"`
4. **Get results** back: `scp pi:/home/pi/project/output/* ./output/`

### Watch and Sync (for active development)

Use fswatch (install via `brew install fswatch`) to auto-sync on save:
```bash
fswatch -o ./project | xargs -n1 -I{} rsync -avz --exclude='.git' ./project/ pi:/home/pi/project/
```

## Service Management (systemd)

```bash
# Check service status
ssh pi "sudo systemctl status myservice"

# Restart service
ssh pi "sudo systemctl restart myservice"

# View logs
ssh pi "sudo journalctl -u myservice -n 50 --no-pager"

# Follow logs (streaming)
ssh pi "sudo journalctl -u myservice -f"
```

## Common Pi Operations

### System Info
```bash
ssh pi "hostname && uname -a"
ssh pi "cat /etc/os-release"
ssh pi "vcgencmd measure_temp"  # CPU temperature
ssh pi "df -h"                   # Disk usage
ssh pi "free -h"                 # Memory usage
```

### GPIO (requires RPi.GPIO or gpiozero)
```bash
ssh pi 'python3 -c "
from gpiozero import LED
from time import sleep
led = LED(17)
led.on()
sleep(1)
led.off()
"'
```

### Package Management
```bash
ssh pi "sudo apt update && sudo apt upgrade -y"
ssh pi "sudo apt install -y python3-pip"
ssh pi "pip3 install --user requests"
```

## Troubleshooting

### Connection Issues
```bash
# Test connection
ssh -v pi

# Check if Pi is reachable
ping raspberrypi.local

# Verify SSH config
cat ~/.ssh/config | grep -A5 "Host pi"
```

### Command Escaping Issues
If commands behave unexpectedly:
1. Test locally first: `echo 'your command'`
2. Use `bash -x` for debugging: `ssh pi 'bash -x -c "your command"'`
3. For complex quoting, use heredocs instead

### Slow Transfers
```bash
# Use compression for text-heavy transfers
rsync -avz --compress-level=9 ./project/ pi:/home/pi/project/

# Use faster cipher for large files on local network
scp -c aes128-ctr largefile.bin pi:/home/pi/
```

## SSH Configuration

The `pi` alias should be configured in `~/.ssh/config`:

```
Host pi
    HostName raspberrypi.local   # or IP address
    User pi
    IdentityFile ~/.ssh/id_rsa   # optional if using default key
```

See @references/configuration.md for detailed SSH setup.
