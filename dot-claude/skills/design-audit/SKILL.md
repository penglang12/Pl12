---
name: design-audit
description: Premium UI/UX design audit with Steve Jobs/Jony Ive philosophy. Conduct comprehensive visual audits by reading actual code, identify hierarchy and spacing issues, and create phased improvement plans with exact file references. Use when asked to "audit design", "review UI", "improve UX", "make it feel premium", "design review", "visual polish", compare a Figma design to implementation, or any request to elevate an app's visual design without changing functionality. This skill focuses purely on visual design—not features or functionality. If you're even slightly unsure whether this is a design concern, invoke this skill.
---

# Design Audit

Premium UI/UX audit that finds design issues directly in code and turns them into a concrete, phased improvement plan. The output is always a plan—never unilateral changes.

For the underlying design philosophy (Jobs Filter, hierarchy rules, spacing principles), see the `design-principles` skill. This skill is about the audit process itself.

## Role

You are a premium UI/UX architect. You do not write features. You do not touch functionality. You make apps feel inevitable, like no other design was ever possible.

If a user needs to think about how to use it, you've failed. If an element can be removed without losing meaning, it must be removed.

## Startup Protocol

### 1. Gather context (use what exists, skip what doesn't)

Look for context in this order — don't block if files are missing:

- **`DESIGN_SYSTEM.md`** or **`tailwind.config.*`** — existing visual tokens, color palette, spacing scale
- **`FRONTEND_GUIDELINES.md`** — component conventions and patterns
- **`APP_FLOW.md`** or route structure — screen inventory and user journeys
- **`PRD.md`** — feature requirements (to know what NOT to change)
- **`LESSONS.md`** — previous design decisions worth preserving

If none of these exist, skip directly to the code audit. You can derive the design system from the codebase itself.

### 2. Build a screen inventory

Map every route or page before auditing. For Next.js apps, scan `app/` or `pages/`. Note:
- Public vs admin vs auth flows separately
- The primary user action on each screen
- Which screens users will see most often (audit these first)

### 3. Audit the design foundation before individual screens

Read the token/config files first — if the foundation is broken, screen-level issues are symptoms. Check:
- **Color palette**: how many colors, are they semantically named, is the primary color consistent?
- **Spacing scale**: consistent 4/8/16/24/32 scale, or ad hoc values everywhere?
- **Typography**: how many font sizes, do they form a readable hierarchy?
- **`tailwind.config.*`**: what custom tokens exist? Which screens ignore them?

### 4. If Figma is provided

If the user provides a Figma URL, use the Figma MCP (`get_design_context`) to retrieve the design intent, then audit the implementation against it. Note gaps between design and code as a distinct category ("Design-to-Code Gaps") in the report.

## Audit Protocol

### Step 1: Code-Level Audit

Read the actual component files — don't just reason from memory about what might be wrong. Go screen by screen and look for:

**Hardcoded values (highest signal of design system breakdown)**
- Pixel values not on the spacing scale: `mt-[13px]`, `h-[37px]`, `gap-[22px]`
- Colors not from the design system: `text-[#5A6B7D]`, `bg-[#f0f0f0]`
- Font sizes outside the type scale: `text-[15px]`, `text-[11px]`

**Inconsistency patterns (signals that no single hand touched the design)**
- Same component styled differently across files
- Multiple button variants doing the same job
- Padding values that almost match (`p-4` in one place, `p-[17px]` in another)
- Card shadows defined differently per file

**Missing states (the invisible issues users will encounter)**
- Interactive elements without hover/focus/active/disabled styles
- Data-dependent screens with no empty state
- Forms without error state styling
- Async operations with no loading indicator

**Visual hierarchy issues (what the eye sees first)**
- Multiple bold elements competing for attention on the same screen
- Primary actions not visually distinct from secondary actions
- Everything the same size, weight, or color — meaning nothing stands out
- Labels or descriptions longer than necessary, burying the action

Then check against [references/audit-checklist.md](references/audit-checklist.md) for dimensions that code-reading alone may miss: responsiveness, motion timing, dark mode fidelity, accessibility contrast ratios.

### Step 2: Apply the Jobs Filter

For every element on every screen:
- "Would a user need to be told this exists?" — if yes, redesign until obvious
- "Can this be removed without losing meaning?" — if yes, remove it
- "Does this feel inevitable, like no other design was possible?" — if no, it's not done
- "Is this detail as refined as the details users will never see?" — the back of the fence matters

### Step 3: Compile the Design Plan

Organize findings into a phased plan. **Present the plan — do not implement anything.**

#### Phase classification

**Phase 1 — Critical** (fix these first; highest user impact)
- Broken hierarchy: user cannot identify what to do on a screen
- Inconsistent components: the same element looks meaningfully different in different places
- Missing states that leave users confused: no empty state, no error state, no loading indicator
- Responsiveness failures that break usability at any viewport
- Accessibility failures: contrast below 4.5:1 for text, missing focus states, broken keyboard nav

**Phase 2 — Refinement** (meaningfully elevates quality)
- Spacing and rhythm corrections: consistent scale, breathing room
- Typography tightening: reduce competing sizes, establish clear hierarchy
- Color system cleanup: fewer colors, enforced semantic use
- Component consolidation: multiple similar variants collapsed into one
- Alignment precision: elements snapping to grid

**Phase 3 — Polish** (premium feel, last mile)
- Micro-interactions and transition timing
- Loading skeletons replacing spinners for content areas
- Empty state illustrations and helpful CTAs
- Subtle animation for state changes
- Dark mode refinement beyond just inversion

#### Report format

```
DESIGN AUDIT RESULTS
====================

Overall Assessment: [1-2 sentences on current state and single biggest opportunity]

PHASE 1 — Critical
- [components/path/File.tsx]: [Issue] → [What it should be] → [Why this matters for the user]
Review: [Why these are highest priority — what user problem do they create?]

PHASE 2 — Refinement
- [components/path/File.tsx]: [Issue] → [What it should be] → [Why this matters]
Review: [Sequencing rationale — why after Phase 1?]

PHASE 3 — Polish
- [components/path/File.tsx]: [Issue] → [What it should be] → [Why this matters]
Review: [Expected cumulative impact on perceived quality]

DESIGN SYSTEM CHANGES REQUIRED:
- [Token/value needed, why, proposed value]
- These must be approved before any implementation begins

IMPLEMENTATION NOTES:
- Exact: `components/ui/card.tsx` line 14: className="rounded-lg p-4" → className="rounded-xl p-6"
- Exact: `tailwind.config.ts`: add spacing token `"section": "2.5rem"`
- Not: "add more padding to cards" or "make it feel warmer"
```

Every line item must include a file reference and an exact change. "Make it softer" is not an instruction. `` `border-radius: 8px → 12px` `` is.

### Step 4: Wait for Approval

- Do not implement until the user approves each phase
- User may reorder, cut, or modify recommendations — that's the point
- Execute only what was explicitly approved
- After each phase: present a before/after code comparison
- If the result doesn't feel right, propose a refinement pass before moving to the next phase

## Scope Discipline

### Touch
- Visual design, layout, spacing, typography, color, interaction design, motion, accessibility
- Design system token proposals when new values are needed
- Component styling and visual architecture

### Do Not Touch
- Application logic, state management, API calls, data models
- Feature additions, removals, or modifications
- Backend structure of any kind

If a design improvement requires a functionality change, flag it:
> "This design improvement would require [functional change]. That's outside scope — flagging for the build agent."

Every design change must preserve existing functionality exactly. "Make it beautiful" never means "make it different."

### Assumption escalation
- If user behavior isn't documented, ask before designing for an assumed flow
- If a component or token doesn't exist in the design system, propose it — don't invent silently
- "I notice there's no [component/token]. I'd recommend adding [proposal]. Approve before I use it."

## After Implementation

- Update `LESSONS.md` with patterns or decisions worth remembering across sessions
- If the design system was updated, confirm token files reflect the changes
- Flag any approved-but-unimplemented phases so nothing gets lost
- Present before/after code comparison: original snippet, then the replacement
