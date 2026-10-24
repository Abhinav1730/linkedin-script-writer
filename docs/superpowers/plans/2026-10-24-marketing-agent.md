# Marketing agent implementation plan
Goal: independently scheduled evidence-grounded SmartMeet LinkedIn drafts with screenshot email.
Spec: ../specs/2026-10-24-marketing-agent.md

1. Write failing tests for free-only model policy, draft schema/factual limits, feature rotation, duplicate slots, email ambiguity and attachment privacy.
2. Implement Python state/orchestration, isolated Hermes worker and controlled browser capture; enforce allowlisted routes, demo identity and no meeting creation.
3. Add demo account provisioning, feature inventory, deployment timer, secret-free configuration, operational documentation and examples.
4. Verify controlled end-to-end mail/inference tests; run real demo capture and free inference if credentials work; review complete change, push main and activate independent timer only after first draft evidence succeeds.

Review focus: paid fallback; untrusted UI instructions; authenticated-route leakage; SMTP/API timeout ambiguity; unavailable feature evidence. Each must fail closed.
