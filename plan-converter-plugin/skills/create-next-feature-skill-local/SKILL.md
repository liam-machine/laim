---
name: create-next-feature-skill-local
description: >
  Create a /next-feature slash command locally in the current project repo. Use when the user
  says "create next-feature command", "set up next-feature", "scaffold next-feature locally",
  "add next-feature to this project", or wants a local slash command to iterate through
  features.json one feature at a time using the feature-dev agent. Requires features.json
  to exist in the project root.
---

# Create /next-feature Locally

Generate a `.claude/commands/next-feature.md` slash command in the current project repo.

## Steps

1. **Verify features.json exists** in project root. If missing, tell the user to create one first (e.g. with the plan-converter skill).

2. **Read features.json** to determine:
   - Project platform (`project.platform` or infer from tech stack)
   - Phase names (for progress display)
   - Whether features use `dependencies` or `prerequisites`

3. **Create `.claude/commands/` directory** if it doesn't exist.

4. **Write `.claude/commands/next-feature.md`** with the content below, substituting `{{DEPENDENCY_KEY}}` with either `dependencies` or `prerequisites` based on what features.json uses.

5. **Confirm** to the user that `/next-feature` is ready. Tell them to start a new session or reload for the command to take effect.

## Generated File Content

Write this exact content to `.claude/commands/next-feature.md`:

````markdown
---
description: Implement the next feature from features.json
argument-hint: Optional feature ID (e.g. F102)
---

Read `features.json`. If `$ARGUMENTS` has a feature ID, select that feature. Otherwise auto-select the first feature where `status` is `"pending"`, `skip` is not `true`, and all `{{DEPENDENCY_KEY}}` are `"completed"` (in ID order).

If no feature is eligible, show progress summary and stop.

Display the selected feature (ID, name, phase, description, implementation_notes, validation_criteria).

Invoke the feature-dev skill to implement it — pass the feature description, implementation_notes, and validation_criteria as context.

After implementation, validate each `validation_criteria` entry:
- "Verify in Chrome:" → use claude-in-chrome browser tools
- "Verify in iOS Simulator:" → use iOS Simulator
- "Verify in Android Emulator:" → use Android Emulator
- Other criteria → run appropriate build/test commands

If validation fails, fix and re-validate.

Once all criteria pass:
1. Set feature `status` to `"completed"` in features.json
2. If all features in the phase are completed, set phase `status` to `"completed"`
3. Git commit (do NOT push): `Implement [ID]: [Name]\n\n[summary]\n\nCo-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>`

Then display progress:

```
✓ COMPLETED: [ID] — [Name]
[Summary of what was built]

Progress: [completed]/[total] ([%]%) — skipped: [count]
[██████░░░░ 60%]

By phase:
  [phase name]: [x]/[y] ([%]%)
  ...

Next: [ID] — [Name] ([phase], [effort])
Run /next-feature to continue.
```
````
