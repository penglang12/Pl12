---
name: coding-standards
description: >
  Template skill that enforces team coding patterns in every dev session.
  Ships with [FILL IN] placeholders — a Lead populates it once per project.
  Covers Frontend, Backend, ML/Data, and QA role sections with required patterns,
  anti-patterns, file structure rules, and do-not-do lists.
  Triggers on: coding standards, pattern questions, dev session start.
triggers:
  - coding standards
  - what's our pattern
  - how should I structure
  - code conventions
  - anti-patterns
---

# Coding Standards Skill

You enforce this team's coding standards in every development session.
When a developer asks about patterns, always answer from these standards first.
If a pattern isn't covered here, flag it for the Lead to add after the session.

---

## How to Use This Skill

**For Leads:** Replace all `[FILL IN — example]` placeholders with your team's actual standards before publishing this skill to developers. Each section has examples to guide you — delete the examples and write your own.

**For Developers:** This skill auto-loads your team's standards. Ask Claude "what's our pattern for X?" and it will answer from these standards. If Claude says a pattern "isn't in coding-standards yet", flag it to your Lead.

---

## Frontend Standards

### Required Patterns

```
[FILL IN — e.g., "Always use React Query for server state. Never use useState to store fetched data."]
[FILL IN — e.g., "All components must be typed with explicit props interfaces, never inline object types."]
[FILL IN — e.g., "Use Tailwind utility classes only. No inline styles, no CSS modules."]
[FILL IN — e.g., "Forms must use React Hook Form + Zod schema validation."]
```

### Anti-Patterns

```
[FILL IN — e.g., "Never use useEffect to fetch data — use React Query."]
[FILL IN — e.g., "Never use any type in TypeScript."]
[FILL IN — e.g., "Never mutate state directly — always use setState or Zustand setters."]
```

### File Structure Rules

```
[FILL IN — e.g., "One component per file. File name matches component name exactly."]
[FILL IN — e.g., "Co-locate tests: Button.tsx → Button.test.tsx in same directory."]
[FILL IN — e.g., "Shared UI goes in src/components/ui/. Feature-specific in src/features/[name]/components/"]
```

### Do Not Do

```
[FILL IN — e.g., "Do not create barrel exports (index.ts re-exports) — import directly from the file."]
[FILL IN — e.g., "Do not add console.log in production code — use the logger utility."]
[FILL IN — e.g., "Do not call API endpoints directly from components — always go through a service or React Query hook."]
```

---

## Backend Standards

### Required Patterns

```
[FILL IN — e.g., "All request bodies validated with Zod schemas at the route handler level."]
[FILL IN — e.g., "Database access through repository classes only — no raw Prisma calls in route handlers."]
[FILL IN — e.g., "All endpoints must return typed responses matching the OpenAPI spec."]
[FILL IN — e.g., "Use structured error classes (AppError, ValidationError) — never throw raw strings."]
```

### Anti-Patterns

```
[FILL IN — e.g., "Never use any in TypeScript."]
[FILL IN — e.g., "Never write raw SQL — use Prisma query builder."]
[FILL IN — e.g., "Never handle auth logic inside a route handler — use middleware."]
```

### File Structure Rules

```
[FILL IN — e.g., "Routes in src/routes/. Services in src/services/. Repositories in src/repositories/."]
[FILL IN — e.g., "One router file per domain (users.router.ts, billing.router.ts)."]
[FILL IN — e.g., "Middleware in src/middleware/. One file per middleware."]
```

### Do Not Do

```
[FILL IN — e.g., "Do not expose internal error messages to API responses — use generic messages with error codes."]
[FILL IN — e.g., "Do not store secrets in code — all secrets from environment variables."]
[FILL IN — e.g., "Do not bypass the repository layer for 'quick' queries."]
```

---

## ML / Data Standards

### Required Patterns

```
[FILL IN — e.g., "All data pipelines must have an idempotency check before writing outputs."]
[FILL IN — e.g., "Model versions tracked in MLflow. No untracked model artifacts."]
[FILL IN — e.g., "Input validation on all inference endpoints — reject malformed payloads before model call."]
[FILL IN — e.g., "All training scripts must log: dataset version, hyperparameters, eval metrics."]
```

### Anti-Patterns

```
[FILL IN — e.g., "Never hardcode dataset paths — use config files or environment variables."]
[FILL IN — e.g., "Never commit model weights to git — use artifact storage."]
[FILL IN — e.g., "Never train on unversioned data."]
```

### File Structure Rules

```
[FILL IN — e.g., "Training scripts in src/training/. Inference in src/inference/. Utils in src/utils/."]
[FILL IN — e.g., "One notebook per experiment. Notebooks are for exploration only — production logic goes in .py files."]
[FILL IN — e.g., "Data schemas defined in src/schemas/ using Pydantic."]
```

### Do Not Do

```
[FILL IN — e.g., "Do not use global state in inference code — models must be stateless per request."]
[FILL IN — e.g., "Do not skip evaluation on validation set before promoting a model."]
[FILL IN — e.g., "Do not mix training and inference dependencies in the same environment."]
```

---

## QA Standards

### Required Patterns

```
[FILL IN — e.g., "Test cases must be written before implementation starts (TDD)."]
[FILL IN — e.g., "Every acceptance criterion on a card must have a corresponding test case."]
[FILL IN — e.g., "Bug reports must include: steps to reproduce, expected vs actual, environment, severity."]
[FILL IN — e.g., "Use Given/When/Then format for BDD test cases."]
```

### Anti-Patterns

```
[FILL IN — e.g., "Never mark a card as QA-passed without running the full regression suite for the affected module."]
[FILL IN — e.g., "Never write test cases that only test the happy path — always include at least one error and one edge case."]
[FILL IN — e.g., "Never skip browser matrix testing (Chrome, Firefox, Safari) for frontend changes."]
```

### File Structure Rules

```
[FILL IN — e.g., "Test plans in docs/qa/test-plans/. Test cases in docs/qa/test-cases/."]
[FILL IN — e.g., "Bug reports in docs/qa/bugs/. One file per bug."]
[FILL IN — e.g., "Name test files: TC-[PRD]-[NNN]-[feature].md"]
```

### Do Not Do

```
[FILL IN — e.g., "Do not close a bug without a verified fix and regression test."]
[FILL IN — e.g., "Do not test on localhost only — always test on staging environment."]
[FILL IN — e.g., "Do not skip regression checks on files adjacent to the changed module."]
```

---

## Behavior Rules

- **Answer from standards first** — when a dev asks about a pattern, check these standards before responding
- **Flag uncovered patterns** — if a question isn't answered by these standards, say: "This isn't in coding-standards yet — recommend the Lead add it after this session"
- **Never approve anti-patterns** — if a developer proposes code matching an anti-pattern, flag it clearly and suggest the correct pattern
- **Remind at session start** — when a module context MD is attached, surface the relevant role's standards in the first response
- **Standards > conventions** — if a developer cites a general convention that contradicts these standards, these standards win
