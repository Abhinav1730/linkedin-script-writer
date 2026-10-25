# Broader SmartMeet marketing drafts

## Intent
Generate useful, persuasive LinkedIn marketing that explains why SmartMeet matters to users, rather than making every post a description of an app screenshot.

## Approaches
The user selected a balanced mix of user value, practical advice, modern collaboration and feature demonstrations, with optional screenshots. Alternatives were mostly thought leadership or retaining a screenshot for every draft. The balanced mix provides variety while retaining concrete product evidence.

## Proposed behavior
Rotate five editorial pillars across scheduled slots: user problems and value, practical meeting advice, modern collaboration, audience use cases, and feature demonstrations. Rotate verified product capabilities independently so each post can connect its theme to a relevant SmartMeet capability. Keep the existing free-model writer, independent reviewer and three-hour email schedule, with all three configured recipients.

Use a flexible narrative: an observation or question, a recognizable challenge, practical advice or a clearly hypothetical use case, a relevant verified SmartMeet capability, and a natural invitation to explore. Remove the requirement that every hook and benefit be a question. Keep exact verified product claims in the rendered post without requiring the rest of the story to describe the UI.

Feature demonstrations require a fresh screenshot. Other pillars can send text-only drafts and use the source-owned verified capability catalog as product evidence. The reviewer receives the editorial brief and evidence type and checks advice separately from claims about product behavior. An absent screenshot must never be treated as observed UI.

Discuss modern collaboration as a perspective or hypothetical scenario, without invented prevalence, statistics, news or predictions. Live trend research and automated illustrative image generation are outside this change. Never invent customer stories, testimonials, pricing, measurable results or guarantees.

## Implementation choices
Persist the selected editorial brief with each slot so retries retain the same theme. Preserve existing approved drafts and delivery idempotency. Record evidence type and screenshot availability in the email so reviewers understand the supporting material. Update tests for rotation, text-only delivery, required screenshots for demos, reviewer context and legacy retries, plus documentation and changelog.

## Success
Scheduled emails vary in purpose and narrative, include a clear connection to SmartMeet's verified value, and can deliver a complete marketing draft without an app screenshot. Free providers may still fail or return rejected content; the existing bounded retries and withholding rules continue.
