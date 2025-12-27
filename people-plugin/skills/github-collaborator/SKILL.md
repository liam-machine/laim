---
name: github-collaborator
description: Add or remove GitHub collaborators using contact names. Use this skill when the user wants to "add someone as a collaborator", "add X to my repo", "add X as a collaborator", "give X access to this repo", "add collaborator", "remove collaborator", "invite X to GitHub repo", mentions adding a known contact (like James, JD) as a GitHub collaborator, or says "add X to my active repo". Resolves contact names to GitHub handles using the shared contacts directory.
---

# GitHub Collaborator Skill

Add or remove GitHub collaborators by referencing contacts by name. Resolves names to GitHub handles via the shared contacts directory.

## Quick Start

```
"Add James as a collaborator to my active repo"
"Give JD access to this repository"
"Add James Dowzard as a collaborator with write access"
"Remove James from this repo"
```

## Workflow

### Step 1: Resolve Contact to GitHub Handle

Use the shared contact lookup script:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/messaging/scripts/lookup-contact.py --name "<contact name>"
```

Check the response for a `github` field. If not present, inform the user that the contact doesn't have a GitHub handle configured.

### Step 2: Determine Target Repository

If not explicitly specified, use the current working directory:

```bash
# Get the repo in format owner/repo
gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null
```

If this fails (not in a git repo or no remote), ask the user to specify the repository.

### Step 3: Add Collaborator

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/github-collaborator/scripts/add-collaborator.sh \
  --repo "<owner/repo>" \
  --user "<github_handle>" \
  --permission "<permission>"
```

**Permission levels:**
- `pull` - Read-only access
- `push` - Read and write access (default)
- `admin` - Full administrative access

### Step 4: Confirm to User

Report:
- Contact name resolved to GitHub handle
- Repository the collaborator was added to
- Permission level granted
- Note that the user will receive an email invitation

## Error Handling

- **Contact not found:** Suggest checking spelling or adding the contact
- **No GitHub handle:** Prompt user to update the contact's GitHub username in contacts.yaml
- **Not a git repository:** Ask user to specify the repository
- **Permission denied:** User may not have admin access to the repository
- **User already a collaborator:** Inform user, offer to update permissions

## Contact Configuration

To add a GitHub handle to a contact, edit `${CLAUDE_PLUGIN_ROOT}/skills/messaging/references/contacts.yaml`:

```yaml
- name: James Dowzard
  nicknames:
    - James
    - JD
  github: jamesdowzard  # Add this field
  platforms:
    # ... existing platforms
```

## Scripts

| Script | Purpose |
|--------|---------|
| `add-collaborator.sh` | Add a user as repository collaborator |

Script location: `${CLAUDE_PLUGIN_ROOT}/skills/github-collaborator/scripts/`
