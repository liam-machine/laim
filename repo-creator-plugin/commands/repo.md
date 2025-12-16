---
description: Create a new repository, publish to GitHub, and optionally set up a virtual environment
argument-hint: <repo-name> [work]
allowed-tools: Bash(*), Read, Write, AskUserQuestion
---

# Create Repository Command

You are helping the user create a new repository. Follow these steps carefully:

## Arguments
- `$1` = Repository name (required)
- `$2` = "work" flag (optional) - if present, create in work directory

**Repo name provided:** $ARGUMENTS

## Step 1: Check Configuration

First, check if the configuration file exists:

```bash
cat ~/.claude/repo-creator-config.json 2>/dev/null
```

**If the config file does NOT exist or is empty:**

Use the AskUserQuestion tool to ask the user TWO questions:
1. "What is the absolute path to your PERSONAL projects directory?" (e.g., /Users/username/GIT/personal)
2. "What is the absolute path to your WORK projects directory?" (e.g., /Users/username/GIT/work)

Then create the config file:
```bash
mkdir -p ~/.claude
cat > ~/.claude/repo-creator-config.json << 'EOF'
{
  "personalRepoPath": "<USER_PROVIDED_PERSONAL_PATH>",
  "workRepoPath": "<USER_PROVIDED_WORK_PATH>"
}
EOF
```

## Step 2: Determine Repository Location

Read the config file and determine where to create the repo:
- If `$2` is "work" or "Work" or "WORK", use `workRepoPath`
- Otherwise (default), use `personalRepoPath`

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

## Step 4: Create the Repository

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

**For PERSONAL repos (default):**
Get the user's GitHub username and create the repo:
```bash
gh auth status 2>&1 | grep "Logged in to github.com account"
gh repo create <GITHUB_USERNAME>/<REPO_NAME> --<VISIBILITY> --source=. --remote=origin --push
```

**For WORK repos:**
Use AskUserQuestion to ask: "What GitHub organization should this work repo be published to?"
Then create with that org:
```bash
gh repo create <ORG_NAME>/<REPO_NAME> --<VISIBILITY> --source=. --remote=origin --push
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
