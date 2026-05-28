---
name: context-audit
description: >
  Lead skill for sprint-start context health checks. Reads a module's context MD
  and compares it against the actual files in the repo. Flags missing files, untracked
  new files, dependency drift, pattern drift, and staleness. Outputs a structured audit
  report with CLEAN / STALE / OUTDATED status and a copy-paste ready CONTEXT-HEALTH.md row.
triggers:
  - context-audit
  - audit context
  - context health
  - sprint start audit
  - /context-audit
  - stale context
  - context health check
---

# Context Audit Skill

You are the Lead's sprint-start audit tool. Your job is to compare a module's context MD against the actual codebase and surface every divergence — nothing slips past you.

Run this at the start of every sprint, for every module that will be touched. A stale context MD loaded into a developer session is worse than no context MD at all.

---

## Input

The user provides a module name or context MD path. Examples:
- `auth` → resolve to `docs/context/auth.context.md`
- `docs/context/billing.context.md` → use directly
- `auth.context.md` → use directly

**Resolution order (try in sequence until found):**
1. `docs/context/[module].context.md`
2. `[module].context.md`
3. `docs/[module].context.md`

If none found, stop: "Context MD not found. Please provide the exact file path."

---

## Pre-flight Checks

Before running the audit:

1. **Confirm context MD exists** — if not found after resolution, stop and ask.
2. **Confirm module directory exists** — infer from the "Key Files" directory prefixes. If the directory cannot be determined, warn and mark Check 2 as unable to run (treat as FAIL with note "Module directory could not be determined — Check 2 skipped"). Continue with remaining checks.
3. **Check for `CONTEXT-HEALTH.md`** in project root — if missing, note it at the end and offer a starter template.
4. **Check for "Key Files" section** — if the context MD has no "## Key Files" section, mark Check 1 and Check 2 as unable to run: flag them as FAIL with note "Key Files section not found in context MD."

---

## The 5 Checks

Run all 5 checks. Do not stop at the first failure — collect all findings, then produce the report.

### Check 1 — Missing Files

Read every file listed under "## Key Files" in the context MD.
For each: does the file exist in the repo?

Flag any that are missing. These were once key files and have been deleted, renamed, or moved — the context MD doesn't know yet.

### Check 2 — Untracked Files

Read the module directory (infer it from the directory prefix of "Key Files" entries).
List all `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.go`, `.java`, `.rs` files in the module.
Exclude: `*.test.*`, `*.spec.*`, `__tests__/`, `dist/`, `build/`, `.d.ts`.

Flag any file not listed in "Key Files". New significant files suggest the module has grown beyond what the context MD documents.

### Check 3 — Dependency Drift

Read the import statements in each "Key Files" entry that exists.
Cross-reference against the "## Dependencies" section of the context MD.

Flag any package or internal module that appears in imports but is not listed in "Dependencies". This indicates the module now relies on something the context MD doesn't mention.

### Check 4 — Pattern Drift

Read the "## Required Patterns" section of the context MD.
Scan the actual module files for evidence of each pattern.

Examples:
- Pattern says "always use React Query" → look for `useQuery`/`useMutation` imports
- Pattern says "use Zod for validation" → look for `z.` or `import { z }`
- Pattern says "repository layer only" → look for direct Prisma calls in route files

Flag patterns that are listed as required but show no evidence of use in the actual code. Note this is best-effort — add a ⚠️ Limited scan note below any PASS or FAIL result if the module is large (10+ files).

If the context MD has no "## Required Patterns" section: report "Required Patterns section not found — Check 4 skipped" and treat as PASS.

### Check 5 — Staleness

Read the `last_verified_sprint` field from the context MD frontmatter or header.
Compare to the current sprint (ask the user for the current sprint if not provided in the conversation).

- Same sprint → PASS
- 1 sprint old → PASS with note
- 2+ sprints old → FAIL — flag exact gap

If `last_verified_sprint` is absent entirely: FAIL — note "last_verified_sprint field not found — add it before next sprint."

---

## Output Format

```
## Context Audit — [module-name].context.md
Audited: [today's date]
Sprint: [current sprint, or "unknown — please specify"]

**Status: CLEAN ✅ / STALE ⚠️ / OUTDATED ❌**

---

### Check 1 — Missing Files
[PASS ✅ / FAIL ❌]
[If FAIL:]
  - `[path/to/file.ts]` — listed in Key Files, not found in repo

### Check 2 — Untracked Files
[PASS ✅ / FAIL ❌]
[If FAIL:]
  - `[path/to/new-file.ts]` — found in module, not listed in Key Files

### Check 3 — Dependency Drift
[PASS ✅ / FAIL ❌]
[If FAIL:]
  - `[package-name]` — imported in [file.ts] but not listed in Dependencies

### Check 4 — Pattern Drift
[PASS ✅ / FAIL ❌]
[If FAIL:]
  - "[pattern name]" — listed as required, no evidence found in module files
[Add this line if the module has 10+ files:]
  ⚠️ Limited scan (large module — [N] files). Manual verification recommended for patterns above.

### Check 5 — Staleness
[PASS ✅ / PASS with note ⚠️ / FAIL ❌]
[If PASS with note:]
  - last_verified_sprint: Sprint-XX (1 sprint ago) — update recommended before next session
[If FAIL:]
  - last_verified_sprint: Sprint-XX ([N] sprints ago) — update required

---

### Summary

**Required actions before this context MD is used in a session:**
- [ ] [specific section to update]
- [ ] [specific file to add/remove from Key Files]
- [ ] [specific dependency to add]
- [ ] Update last_verified_sprint to [current sprint]

---

### CONTEXT-HEALTH.md Row (copy-paste ready)

| [module] | [module].context.md | [current sprint] | [owner from MD] | [status emoji] [CLEAN/STALE/OUTDATED] |
```

---

## Status Definitions

| Status | Condition |
|--------|-----------|
| **CLEAN ✅** | All 5 checks pass |
| **STALE ⚠️** | 1-2 checks fail (update before next developer session) |
| **OUTDATED ❌** | 3+ checks fail (do not use as session context until fully updated) |

---

## Behavior Rules

- **Never report CLEAN if any check fails** — even one failure is STALE minimum
- **Never guess the module path** — if resolution fails, stop and ask
- **Always provide the CONTEXT-HEALTH.md row** — copy-paste ready, even on CLEAN audits
- **Check 4 is best-effort** — if the module has 10+ files, add a ⚠️ Limited scan note below any PASS or FAIL result
- **Owner field source** — look for `owner:` in the context MD frontmatter, or a line like `**Owner:** [name]` in the header. If not found, use `[unknown]` and add to Required Actions: "Add owner field to context MD header."
- **One module per audit run** — do not batch across modules in a single session
- **If `CONTEXT-HEALTH.md` is missing**, output a starter template at the end:

```
# CONTEXT-HEALTH.md — [Project Name]
Last reviewed: [current sprint]

| Module | Context MD | Last Verified | Owner | Status |
|--------|-----------|---------------|-------|--------|
| [module] | [module].context.md | [current sprint] | [owner] | [status] |
```
