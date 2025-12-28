# SSH Pi Configuration Guide

## Prerequisites

1. **Raspberry Pi** with SSH enabled
2. **SSH key authentication** configured (password-free login)
3. **Network connectivity** between Mac and Pi

## Step 1: Enable SSH on Raspberry Pi

### Option A: Raspberry Pi Imager (during OS install)
1. In Raspberry Pi Imager, click the gear icon
2. Enable SSH
3. Set username/password
4. Configure WiFi (optional)

### Option B: On existing Pi
```bash
# Connect with keyboard/monitor or via password SSH
sudo raspi-config
# Navigate to: Interface Options → SSH → Enable
```

### Option C: Headless (SD card method)
Create an empty file named `ssh` in the boot partition:
```bash
touch /Volumes/boot/ssh
```

## Step 2: Generate SSH Key (if needed)

On your Mac:
```bash
# Check for existing key
ls ~/.ssh/id_*.pub

# Generate new key if none exists
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter to accept default location
# Optionally set a passphrase
```

## Step 3: Copy SSH Key to Pi

```bash
# Using ssh-copy-id (easiest)
ssh-copy-id pi@raspberrypi.local

# Or manually
cat ~/.ssh/id_ed25519.pub | ssh pi@raspberrypi.local "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

## Step 4: Configure SSH Alias

Add to `~/.ssh/config`:

```
Host pi
    HostName raspberrypi.local
    User pi
    IdentityFile ~/.ssh/id_ed25519
    AddKeysToAgent yes
    UseKeychain yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### Configuration Options Explained

| Option | Purpose |
|--------|---------|
| `HostName` | Pi's address (use IP for reliability) |
| `User` | Login username (default: pi) |
| `IdentityFile` | Path to private key |
| `AddKeysToAgent` | Auto-add key to SSH agent |
| `UseKeychain` | Store passphrase in macOS keychain |
| `ServerAliveInterval` | Keep connection alive (seconds) |
| `ServerAliveCountMax` | Max missed keepalives before disconnect |

### Using Static IP (recommended)

For reliability, assign a static IP to your Pi:

1. Find Pi's MAC address: `ssh pi "cat /sys/class/net/eth0/address"`
2. Set DHCP reservation in router, or
3. Configure static IP on Pi in `/etc/dhcpcd.conf`:

```
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
```

Then update `~/.ssh/config`:
```
Host pi
    HostName 192.168.1.100
    ...
```

## Step 5: Test Connection

```bash
# Test SSH
ssh pi "echo 'Connected to $(hostname)'"

# Expected output: Connected to raspberrypi
```

## Troubleshooting

### "Permission denied (publickey)"
```bash
# Verify key is loaded
ssh-add -l

# Add key if missing
ssh-add ~/.ssh/id_ed25519

# Check Pi's authorized_keys permissions
ssh pi@raspberrypi.local  # with password
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### "Host key verification failed"
```bash
# Remove old host key (if Pi was reinstalled)
ssh-keygen -R raspberrypi.local
ssh-keygen -R 192.168.1.100  # if using IP
```

### "Could not resolve hostname"
```bash
# Try IP address instead
ping raspberrypi.local  # might fail
ping 192.168.1.100       # use actual IP

# Find Pi's IP from router admin page or:
# On Pi: hostname -I
```

### Slow connection
Add to `~/.ssh/config`:
```
Host pi
    ...
    Compression yes
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 600
```

Create sockets directory:
```bash
mkdir -p ~/.ssh/sockets
```

## Security Best Practices

1. **Disable password authentication** on Pi:
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart ssh
   ```

2. **Change default port** (optional):
   ```bash
   # In /etc/ssh/sshd_config
   Port 2222
   ```
   Update `~/.ssh/config`:
   ```
   Host pi
       Port 2222
       ...
   ```

3. **Use fail2ban** to prevent brute-force:
   ```bash
   ssh pi "sudo apt install -y fail2ban"
   ```
