---
description: Create a new repository and publish to GitHub
argument-hint: <repo-name> [org]
---

# Repository Creator

Create repositories with a guided workflow: initialize git, publish to GitHub (personal or organization), and optionally set up a development environment (venv, conda, or npm).

**Arguments:**
- `$1` = Repository name (required)
- `$2` = "org" flag (optional) - if present, create under a GitHub organization

## Workflow

Follow these 7 steps in order:

### Step 1: Check Configuration

Read the configuration file:

```bash
cat ~/.claude/repo-creator-config.json 2>/dev/null
```

**If the config file does NOT exist or is empty:**

Use AskUserQuestion to ask:
- "What is the absolute path to your personal projects directory?" (e.g., `/Users/username/GIT`)

Then create the config:
```bash
mkdir -p ~/.claude
cat > ~/.claude/repo-creator-config.json << 'EOF'
{
  "personalReposPath": "<USER_PROVIDED_PATH>",
  "configuredPaths": ["<USER_PROVIDED_PATH>"]
}
EOF
```

**If the config EXISTS but is missing `configuredPaths`:**

Add the array using the existing `personalReposPath`:
```json
{
  "personalReposPath": "<existing>",
  "configuredPaths": ["<existing>"]
}
```

### Step 2: Determine Repository Location

**If `$2` is "org" (case-insensitive):**
- The path will be determined in Step 4 when the user selects from `configuredPaths`
- Note this is an organization repository

**Otherwise (personal repository):**
- Use `personalReposPath` from config as the repository location

### Step 3: Check GitHub CLI

Verify GitHub CLI is installed and authenticated:

```bash
# Check installation
which gh && gh --version
```

If `gh` is not found:
- On macOS with Homebrew: `brew install gh`
- Otherwise: direct user to https://cli.github.com/

If not authenticated:
- Run `gh auth login` and guide the user through authentication

### Step 3.5: Discover GitHub Organizations (org repos only)

**If `$2` is "org":**

```bash
gh org list 2>/dev/null
```

**If no organizations:** Ask if they want to create a personal repository instead.

**If organizations exist:** Store the list for Step 5.

### Step 4: Create the Repository

**For ORG repos:**

Use AskUserQuestion with `configuredPaths` from config as options:
- "Where would you like to save this repository?"
- Show each path as an option
- Allow "Other" for custom path

If user provides a new path, add it to `configuredPaths` for future use.

**For PERSONAL repos:**

Use `personalReposPath` from config.

---

Create the repository:

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

### Step 5: Publish to GitHub

**First, ask about visibility:**

Use AskUserQuestion: "Should this repository be private or public?"
1. **Private** - Only you (and collaborators) can see this repository
2. **Public** - Anyone on the internet can see this repository

**For PERSONAL repos:**
```bash
gh auth status 2>&1 | grep "Logged in to github.com account"
gh repo create <GITHUB_USERNAME>/<REPO_NAME> --<VISIBILITY> --source=. --remote=origin --push
```

**For ORG repos:**

Use AskUserQuestion with the organizations from Step 3.5:
- "Which organization should this repository be published to?"

Then create:
```bash
gh repo create <SELECTED_ORG>/<REPO_NAME> --<VISIBILITY> --source=. --remote=origin --push
```

### Step 6: Virtual Environment Setup

Use AskUserQuestion: "Would you like to set up a virtual environment?"

1. **venv** - Python virtual environment
2. **conda** - Conda environment
3. **npm** - Node.js project
4. **Skip** - No environment

**For venv:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**For conda:**
Ask for Python version, then:
```bash
conda create -p ./conda-env python=<VERSION> -y
source $(conda info --base)/etc/profile.d/conda.sh && conda activate ./conda-env
```

**For npm:**
```bash
npm init -y
```

### Step 7: Confirm and Activate

```bash
cd <REPO_PATH>/<REPO_NAME>
```

If venv/conda was created, re-activate it.

Confirm to the user:
- Repository created at: `<REPO_PATH>/<REPO_NAME>`
- GitHub URL: `https://github.com/<USERNAME_OR_ORG>/<REPO_NAME>`
- Virtual environment: `<status>` (activated for this session)
- Current working directory is now the new repository
- For future sessions, activate with:
  - venv: `source .venv/bin/activate`
  - conda: `conda activate ./conda-env`

## Error Handling

- **No repo name:** Ask the user for it
- **Directory exists:** Ask for a different name
- **GitHub publishing fails:** Show error, offer retry or skip
- **venv creation fails:** Show error, continue without it
