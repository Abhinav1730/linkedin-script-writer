# Broader Marketing Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deliver a balanced rotation of useful SmartMeet marketing, with optional screenshots.
**Architecture:** Persist a slot-specific editorial brief alongside evidence. Keep the verified capability catalog, strict draft contract and independent review; make screenshot capture mandatory only for demonstrations.
**Tech Stack:** Python, Hermes, Playwright, SQLite, Resend.
**Spec:** docs/superpowers/specs/2026-10-26-marketing-content-design.md

## Global Constraints
Free models only; all three recipients; existing three-hour schedule and delivery idempotency; no invented results, testimonials or current trend facts.

## Review Focus
Legacy cached drafts retain their screenshot requirement. Text-only drafts must not attach stale screenshots. Failed retries retain their brief. Both model roles see the same editorial context. Demonstrations fail closed on missing evidence.

### Task 1: Editorial rotation and delivery
- [x] Add src/editorial.py with five pillar briefs selected from the scheduled slot; persist brief.json before inference.
- [x] Update src/agent.py to create catalog evidence for text-only pillars, require capture for feature demos, pass the brief to both model roles, and omit attachments when absent.
- [x] Update src/hermes_worker.py to allow flexible narratives, practical advice and qualified value framing while checking product claims and unsupported trends.
- [x] Add regression tests for rotation, missing demo screenshots, stale attachments, persisted retry briefs and reviewer context; run npm test.

### Task 2: Real examples and publication
- [x] Generate two local previews with the deployed free models in an isolated state directory; inspect review and draft files.
- [x] Update README, CHANGELOG and remaining_work with verified behavior and limitations.
- [x] Review diff, commit and push main; confirm installed timer still points to this checkout.
