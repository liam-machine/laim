---
description: Implement the next feature (or a specific one) from features.json
argument-hint: Optional feature ID (e.g. F102). If omitted, auto-selects next pending feature.
---

# Next Feature

Implement a feature from `features.json` using the feature-dev agent, validate it, commit the code, and report progress.

## Step 1: Load Features

Read `features.json` from the project root.

If the file does not exist, tell the user to create one first (e.g. by converting a plan.md using the plan-converter skill).

## Step 2: Select Feature

**If `$ARGUMENTS` contains a feature ID** (e.g. `F102`):
- Find that feature in the features array
- If not found, show available feature IDs and ask the user to pick one
- If the feature is already `completed` or `skipped`, warn the user and ask if they want to proceed anyway

**If `$ARGUMENTS` is empty** (auto-select):
1. Find the first feature where ALL of these are true:
   - `status` is `"pending"`
   - `skip` is `false` (or not set)
   - All features listed in `dependencies` have `status: "completed"`
2. Select features in ID order (F001 before F100, F100 before F101, etc.)
3. If no eligible feature exists, report that all features are complete (or blocked) and show the progress summary

## Step 3: Show Feature Context

Before starting implementation, display:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FEATURE: [ID] — [Name]
  Phase: [phase name] | Status: [status] | Effort: [estimated_effort]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Description:
[feature description]

Implementation Notes:
[implementation_notes, or "None" if empty]

Validation Criteria:
- [criterion 1]
- [criterion 2]
- ...

Dependencies: [list or "None"]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 4: Implement with feature-dev

Invoke the feature-dev skill with the feature's description and implementation notes as context. Pass all relevant context so the feature-dev agent can implement without needing to re-read the plan.

The feature-dev agent will handle:
- Codebase exploration (Phase 2)
- Clarifying questions (Phase 3)
- Architecture design (Phase 4)
- Implementation (Phase 5)
- Quality review (Phase 6)

## Step 5: Validate

After implementation, validate against the feature's `validation_criteria`:

**For criteria starting with "Verify in Chrome:"**
- Use Chrome browser automation (claude-in-chrome tools) to navigate, interact, and verify

**For criteria starting with "Verify in iOS Simulator:"**
- Use the iOS Simulator to launch the app and verify

**For criteria starting with "Verify in Android Emulator:"**
- Use the Android Emulator to launch the app and verify

**For all other criteria** (build checks, API tests, CLI output):
- Run the appropriate commands (build, test, curl, etc.)

Go through each validation criterion and confirm it passes. If any criterion fails, fix the issue and re-validate. If a fix requires significant changes, loop back to the feature-dev agent.

## Step 6: Update features.json

After all validation criteria pass:

1. Set the feature's `status` to `"completed"`
2. Update the phase status if all features in that phase are now completed — set the phase `status` to `"completed"`
3. Write the updated `features.json`

## Step 7: Commit

Stage all changed files and create a git commit with the message format:

```
Implement [Feature ID]: [Feature Name]

[1-2 sentence summary of what was built]

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

Do NOT push to remote unless the user explicitly asks.

## Step 8: Progress Summary

After committing, display a progress summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ COMPLETED: [ID] — [Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
[What was built — key files modified, components created, etc.]

━━━━━ Progress ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall: [completed]/[total] features ([percentage]%)
[progress bar: ████░░░░░░ 40%]

By Phase:
  Phase 0 — Foundation:      [x]/[y] ([%]%)
  Phase 1 — MVP:             [x]/[y] ([%]%)
  Phase 2 — Polish:          [x]/[y] ([%]%)
  ...

Skipped: [count] features

━━━━━ Next Up ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Next Feature ID] — [Next Feature Name]
Phase: [phase] | Effort: [effort]
[First line of description]

Run /next-feature to continue, or /next-feature [ID] to jump to a specific feature.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If no more features are pending, display:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🎉 ALL FEATURES COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Overall: [total]/[total] features (100%)
██████████ 100%

All [total] features across [N] phases have been implemented.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Progress Calculation Notes

- **Total** = all features where `skip` is `false`
- **Completed** = features with `status: "completed"` and `skip: false`
- **Skipped** = features with `skip: true` (excluded from percentage)
- **Percentage** = `completed / total * 100`, rounded to nearest integer
- **Progress bar** = 10 blocks, each block represents 10% (█ for filled, ░ for empty)
- **By phase** = group features by `phase` field, show completed/total for each
