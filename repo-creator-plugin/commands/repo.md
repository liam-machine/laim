---
description: Create a new repository, publish to GitHub, and optionally set up a virtual environment
argument-hint: <repo-name> [org]
allowed-tools: Bash(*), Read, Write, AskUserQuestion
---

# Create Repository Command

You are helping the user create a new repository. Follow these steps carefully:

## Arguments
- `$1` = Repository name (required)
- `$2` = "org" flag (optional) - if present, create repository under a GitHub organization

**Repo name provided:** $ARGUMENTS

## Step 1: Check Configuration

First, check if the configuration file exists:

```bash
cat ~/.claude/repo-creator-config.json 2>/dev/null
```

**If the config file does NOT exist or is empty:**

Use the AskUserQuestion tool to ask the user:
- "What is the absolute path to your base projects directory?" (e.g., /Users/username/GIT)
- "What is the subfolder name for personal repos?" (e.g., LIAM)
- "What is the subfolder name for work repos?" (e.g., JHG)

Then create the config file:
```bash
mkdir -p ~/.claude
cat > ~/.claude/repo-creator-config.json << 'EOF'
{
  "basePath": "<BASE_PATH>",
  "personalReposPath": "<BASE_PATH>/<PERSONAL_FOLDER>",
  "workReposPath": "<BASE_PATH>/<WORK_FOLDER>",
  "forksPath": "<BASE_PATH>/FORKS",
  "orgPaths": {}
}
EOF
```

**If the config file EXISTS**, read it and use its values.

## Step 2: Determine Repository Category

**If `$2` is "org" (case-insensitive):**
- Skip this step — the org workflow handles location in Step 5
- Note that this is an organization repository

**Otherwise, ask the user where this repo belongs:**

Use AskUserQuestion: "What type of repository is this?"

Options:
1. **Personal** — Saved to `personalReposPath` (e.g., GIT/LIAM/)
2. **Work** — Saved to `workReposPath` (e.g., GIT/JHG/)

Set `REPO_PATH` to the selected path from the config.

## Step 3: Check GitHub CLI

Check if GitHub CLI is installed:
```bash
which gh
```

If `gh` is not found, install it:
```bash
brew install gh
```

If brew is not available, inform the user they need to install GitHub CLI manually from https://cli.github.com/

Verify gh is authenticated:
```bash
gh auth status
```

If not authenticated, run `gh auth login` and guide the user through authentication.

## Step 3.5: Discover GitHub Organizations (for org repos only)

**If `$2` is "org" (case-insensitive):**

Fetch the user's GitHub organizations:
```bash
gh org list 2>/dev/null
```

This returns a list of organizations the user belongs to.

**If the user has NO organizations:**
- Inform them they don't belong to any GitHub organizations
- Ask if they want to create a personal repository instead
- If yes, go back to Step 2

**If the user HAS organizations:**
- Store the list for use in Step 5 when publishing

## Step 4: Create the Repository

**For ORG repos (when `$2` is "org"):**

First, ask the user which organization to publish to using AskUserQuestion.
Present the organizations discovered in Step 3.5 as options.

Then determine the local path:
- Check if `orgPaths` in the config has a mapping for the selected org name
- If yes, use that path as `REPO_PATH`
- If no, create a new folder at `<basePath>/<ORG_NAME>/` and update the config's `orgPaths` to include it

**For PERSONAL or WORK repos:**

`REPO_PATH` was already set in Step 2.

---

Create the repository directory and initialize git:

```bash
# Create directory
mkdir -p <REPO_PATH>/<REPO_NAME>
cd <REPO_PATH>/<REPO_NAME>

# Initialize git
git init

# Create README
echo "# <REPO_NAME>" > README.md

# Initial commit
git add README.md
git commit -m "Initial commit"
```

## Step 5: Publish to GitHub

**First, ask about repository visibility:**
Use AskUserQuestion to ask: "Should this repository be private or public?"

Provide these options:
1. **Private** - Only you (and collaborators you add) can see this repository
2. **Public** - Anyone on the internet can see this repository

Use `--private` or `--public` flag based on the user's choice.

**For PERSONAL or WORK repos (non-org):**
Get the user's GitHub username and create the repo:
```bash
gh auth status 2>&1 | grep "Logged in to github.com account"
gh repo create <GITHUB_USERNAME>/<REPO_NAME> --<VISIBILITY> --source=. --remote=origin --push
```

**For ORG repos (when `$2` is "org"):**
Create with the selected org (already chosen in Step 4):
```bash
gh repo create <SELECTED_ORG>/<REPO_NAME> --<VISIBILITY> --source=. --remote=origin --push
```

## Step 6: Virtual Environment Setup

Use AskUserQuestion to ask: "Would you like to set up a virtual environment?"

Provide these options:
1. **venv** - Python virtual environment (python3 -m venv .venv)
2. **conda** - Conda environment
3. **npm** - Node.js project (npm init)
4. **Skip** - No virtual environment

Based on the user's choice:

**For venv:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
The virtual environment is now activated for this session.

**For conda:**
Ask for Python version preference, then:
```bash
conda create -p ./conda-env python=<VERSION> -y
source $(conda info --base)/etc/profile.d/conda.sh && conda activate ./conda-env
```
The conda environment is now activated for this session.

**For npm:**
```bash
npm init -y
```
This creates a package.json for Node.js projects.

**For Skip:**
No action needed.

## Step 7: Set Working Directory and Confirm Activation

After everything is complete, ensure you are in the new repository directory with the virtual environment activated:

```bash
cd <REPO_PATH>/<REPO_NAME>
```

If a virtual environment was created, re-activate it to ensure it's active:
- **For venv:** `source .venv/bin/activate`
- **For conda:** `source $(conda info --base)/etc/profile.d/conda.sh && conda activate ./conda-env`

Verify the environment is activated by checking the Python/Node path if applicable.

Confirm to the user:
- Repository created at: `<REPO_PATH>/<REPO_NAME>`
- GitHub URL: `https://github.com/<USERNAME_OR_ORG>/<REPO_NAME>`
- Virtual environment: <status> (activated for this session)
- Current working directory is now the new repository
- For future terminal sessions, activate with:
  - venv: `source .venv/bin/activate`
  - conda: `conda activate ./conda-env`

## Error Handling

- If repo name is not provided, ask the user for it
- If directory already exists, ask if they want to use a different name
- If GitHub publishing fails, show the error and offer to retry or skip
- If venv creation fails, show the error and continue without it
