---
name: create-next-feature-skill-local
description: >
  Create a /next-feature skill locally in the current project repo. Use when the user
  says "create next-feature", "set up next-feature", "scaffold next-feature locally",
  "add next-feature to this project", or wants a local skill to iterate through
  features.json using the feature-dev agent. Requires features.json in the project root.
---

# Create /next-feature Skill Locally

Generate a `.claude/skills/next-feature/SKILL.md` in the current project.

## Steps

1. **Verify features.json exists** in project root. If missing, tell the user to create it first (e.g. with the plan-converter skill).

2. **Read features.json** to determine whether features use `dependencies` or `prerequisites`.

3. **Create `.claude/skills/next-feature/`** directory.

4. **Write `.claude/skills/next-feature/SKILL.md`** with the content below, substituting `{{DEPENDENCY_KEY}}` with `dependencies` or `prerequisites` based on what features.json uses.

5. **Confirm** to the user that `/next-feature` is ready. Skills hot-reload — no restart needed.

## Generated File Content

Write this exact content to `.claude/skills/next-feature/SKILL.md`:

````markdown
---
name: next-feature
description: >
  Implement the next feature from features.json using the feature-dev skill.
  Invoke with /next-feature or /next-feature F102 for a specific feature.
---

Read `features.json`. If `$ARGUMENTS` has a feature ID, select it. Otherwise auto-select the first feature where `status` is `"pending"`, `skip` is not `true`, and all `{{DEPENDENCY_KEY}}` are `"completed"` (in ID order). If none eligible, show progress summary and stop.

Display the selected feature (ID, name, phase, description, implementation_notes, validation_criteria), then invoke the feature-dev skill with the description, implementation_notes, and validation_criteria as context.

After implementation, validate each `validation_criteria` entry:
- "Verify in Chrome:" → use claude-in-chrome browser tools
- "Verify in iOS Simulator:" → use iOS Simulator
- "Verify in Android Emulator:" → use Android Emulator
- Other → run appropriate build/test commands

Fix and re-validate on failure.

Once all criteria pass:
1. Set feature `status` to `"completed"` in features.json
2. If all phase features are done, set phase `status` to `"completed"`
3. Git commit (do NOT push): `Implement [ID]: [Name]\n\n[summary]\n\nCo-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>`

Display progress — exclude `skip: true` features from totals:

```
✓ [ID] — [Name]
[Summary of what was built]

Progress: [completed]/[total] ([%]%) — skipped: [count]
[██████░░░░ 60%]

By phase:
  [phase name]: [x]/[y] ([%]%)
  ...

Next: [ID] — [Name] ([phase], [effort])
/next-feature to continue.
```
````
