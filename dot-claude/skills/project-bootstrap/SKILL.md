---
name: project-bootstrap
description: >
  Two-mode Lead skill for project initialization. BOOTSTRAP: interview-driven — Lead answers
  questions about a new project and the skill generates ARCHITECTURE.md, stub context MDs per
  module, and a starter CONTEXT-HEALTH.md. ONBOARD: scan-driven — scans an existing codebase,
  infers stack, modules, and patterns, then interviews Lead to fill gaps. Both modes produce
  the same three output files. Run once per new project or when onboarding a legacy codebase
  into the Claude Code workflow.
triggers:
  - project bootstrap
  - bootstrap project
  - new project setup
  - create architecture
  - generate context MDs
  - onboard project
  - onboard codebase
  - /project-bootstrap
  - architecture.md
  - setup workflow
---

# Project Bootstrap Skill

You are the Lead's project initialization tool. Your job is to produce three files that every
other skill in the workflow depends on: `ARCHITECTURE.md`, a context MD per module, and
`CONTEXT-HEALTH.md`. Nothing else in the workflow runs correctly without these.

Run this once at the start of every new project, and once when onboarding an existing codebase
into the Claude Code workflow.

---

## Mode Detection

Read the conversation context and apply the first matching rule:

| Signal | Mode |
|--------|------|
| User says "existing project", "legacy", "onboard", provides a repo path | **ONBOARD** |
| Non-empty source files found in `src/`, `app/`, `lib/`, `server/`, `api/`, `backend/`, `frontend/` (and user has not stated "new project") | **ONBOARD** |
| No code found, user says "new project", "from scratch", "starting fresh" | **BOOTSTRAP** |
| Ambiguous | Ask ONE question: "Do you have an existing codebase I should scan, or are we starting from scratch?" |

---

## Mode 1 — BOOTSTRAP

**When:** New project with no existing codebase.

Conduct a structured interview in 3 rounds. Ask 2-3 questions per round — never all at once.

### Round 1 — Project Foundation

1. What is the project name and what type of system is it? (web app, API, mobile app, CLI tool, full-stack, etc.)
2. What is the tech stack? (FE framework, BE framework, database, key external services)
3. What is the hosting/infra approach? (self-hosted, cloud provider, serverless, hybrid)

### Round 2 — Module Breakdown

4. What are the main domains or areas of the system? List them — for example: auth, billing, dashboard, notifications, admin, API.
5. For each module named: who owns it (FE / BE / QA / DevOps) and what is it responsible for?
6. Which files or areas require Lead approval before any developer can touch them?

### Round 3 — Team and Constraints

7. What is the team composition? (how many FE, BE, QA, DevOps developers)
8. Are there hard constraints — legal, compliance, performance, or existing integrations that affect design?
9. Are any patterns already decided team-wide? (e.g., "we always use Zod for validation", "Prisma only, no raw SQL")

After Round 3, generate all three output files.

---

## Mode 2 — ONBOARD

**When:** Existing codebase. Scan first, then interview to fill what can't be inferred.

### Scan Sequence

Run these scans before asking a single question:

**Step 1 — Detect stack**
Look for: `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `composer.json`, `Gemfile`.
Infer: primary language, framework, test runner, key dependencies.

**Step 2 — Map modules**
Read the top-level directory structure. Identify modules from directory names under `src/`, `app/`, `packages/`, `services/`, `apps/`, or the root.
For monorepos: treat each package/app as a separate module.

**Step 3 — Infer patterns**
Read 2-3 key files per module (entry points, largest files, router/controller files).
Look for: import patterns, validation libraries, ORM usage, naming conventions, folder organization rules.

**Step 4 — Check existing context MDs**
Look for `*.context.md` files anywhere in the project. Note which modules already have them.
- **Modules with existing context MDs:** Do not regenerate the file. In `CONTEXT-HEALTH.md`, list them with status `⚠️ Pre-existing — Lead should verify` and their current owner if readable.
- **Modules without context MDs:** Generate new stubs using the output templates below.

### Interview to fill gaps

After the scan, report what was found, then ask the Lead to fill what couldn't be inferred:

```
Scan complete. Here's what I found:

Stack: [inferred stack]
Modules found: [list]
Patterns inferred: [list]

To complete the context MDs, I need a few things:
1. Owner (role) for each module — who is responsible?
2. Do-not-touch files per module — what requires Lead approval to modify?
3. Known gotchas per module — race conditions, quirks, legacy landmines to flag
4. Any required patterns not visible in the code?
```

Ask module by module if the list is long — do not dump all questions at once.

---

## Output Files (Both Modes)

Generate all three files after the interview is complete.

### 1. `ARCHITECTURE.md` (project root)

```markdown
# ARCHITECTURE.md — [Project Name]
Version: 1.0
Last updated: [today's date]
Updated by: [Lead name if provided, otherwise "Lead"]

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | [framework or N/A] |
| Backend | [framework or N/A] |
| Database | [db or N/A] |
| Infrastructure | [hosting/infra] |

## Modules

| Module | Owner Role | Context MD | Notes |
|--------|-----------|-----------|-------|
| [module] | [FE/BE/QA/DevOps] | docs/context/[module].context.md | [brief purpose] |

## Key Boundaries

**Requires Lead approval before modification:**
- [file or directory path]

**Shared modules (used across multiple roles):**
- [module name] — [what it provides]

**External integrations:**
- [service] — [what it does, which module owns it]

## Patterns Enforced Across All Modules

- [pattern]

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | [today] | Initial bootstrap |
```

### 2. `docs/context/[module].context.md` (one per module)

Create the `docs/context/` directory if it doesn't exist. One file per module.

```markdown
# [module-name].context.md
last_verified_sprint: UNVERIFIED — Lead must sign before Sprint 1
owner: [name or role]
prd_ref: —

## Key Files
[List exact file paths discovered from scan, or TO FILL if new project]

## Dependencies
[List inferred from imports, or TO FILL if new project]

## Do Not Touch
[TO FILL — Lead must specify which files require Lead approval]

## Gotchas
[List inferred from code comments and patterns, or TO FILL if new project]

## Required Patterns
[List inferred from codebase, or TO FILL if new project]
```

### 3. `CONTEXT-HEALTH.md` (project root)

```markdown
# CONTEXT-HEALTH.md — [Project Name]
Last reviewed: UNVERIFIED — Lead must sign before Sprint 1

| Module | Context MD | Last Verified | Owner | Status |
|--------|-----------|---------------|-------|--------|
| [module] | docs/context/[module].context.md | UNVERIFIED | [owner] | ⚠️ Stub — needs Lead sign-off |
```

---

## Post-Generation Checklist

After generating all files, always remind the Lead:

```
Bootstrap complete. Three files generated:
- ARCHITECTURE.md
- docs/context/[N] context MDs
- CONTEXT-HEALTH.md

Before Sprint 1 can start:
- [ ] Review each context MD — fill all [TO FILL] fields
- [ ] Sign last_verified_sprint on every context MD (replace UNVERIFIED with Sprint-01)
- [ ] Update CONTEXT-HEALTH.md status to ✅ Fresh for signed modules
- [ ] Share ARCHITECTURE.md with the team before first cards are created

Until last_verified_sprint is signed, no cards should be created against these modules.
```

---

## Behavior Rules

- **Never generate context MDs without module name** — ask if missing before generating. If the Lead cannot provide an owner yet, use `[TO FILL]` and note that owner must be assigned before `last_verified_sprint` can be signed
- **ONBOARD: always state what was inferred vs what the Lead provided** — never mix them silently
- **`[TO FILL]` markers are required** on every field that couldn't be determined — never guess
- **Never overwrite existing context MDs** in ONBOARD mode unless explicitly asked
- **Do not mark `last_verified_sprint` as a real sprint** — always use `UNVERIFIED` until the Lead explicitly signs off
- **When the Lead signs off `last_verified_sprint`**, record the value in the format `Sprint-NN` (e.g., `Sprint-01`, `Sprint-02`) — accept only this format to ensure consistency across context MDs
- **Context MDs go in `docs/context/`** by default — ask Lead if they prefer a different location
- **ARCHITECTURE.md goes in the project root** — always
- **One module per context MD** — never combine two modules in one file
