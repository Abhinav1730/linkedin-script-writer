# Verification and competing failure hypotheses

Run `npm test`. All automated email/inference orchestration tests use controlled providers, a temporary SQLite database, synthetic evidence and fake keys. Browser policy tests use an isolated Chromium page with no network. Real capture verification uses the dedicated demo account; synthetic meeting/recap/Canvas fixtures cannot write to the real meeting APIs. The first operational example email is separate from controlled tests.

| Hypothesis | Evidence/check |
|---|---|
| Paid model or automatic billing fallback | Reject paid IDs; Hermes gets only a free model, `fallback_model=None`, no toolsets; inspect isolated worker test. |
| Model adds inflated sales/price/offline claims | Negative schema and factual-bound tests; exact source claims inserted by renderer; separate-context reviewer. |
| UI instructions/private content enter model evidence | Visible-only DOM extraction test excludes hidden/private/alert/script/form content and redacts email/links. |
| Wrong account/customer screenshot | Dedicated identity checked after login; allowlisted paths; isolated browser storage; synthetic data for private meeting/Canvas views. |
| Auth redirect is captured as a feature | Path/anchor/evidence-term assertions; full deployed screenshot sweep. |
| Writer or review failure still emails | Controlled orchestration rejects before provider call. |
| Preview regenerates before delivery | Cached validated draft and review are promoted. |
| Definite pre-send failures cannot recover | Failed slot retry regression. |
| Duplicate email on concurrency/restart | Process lock, unique slot state, stable provider idempotency; repeat sent slot returns without send. |
| Timeout causes blind resend | Mark delivery_unknown; repeated slot cannot resend automatically. |
| Duplicate draft bypass on retry | Duplicate rejection repeated on cached approved-artifact retry. |
| Hermes free-provider stream loses final JSON | Batch non-streaming transport, single-call iteration budget, one API attempt per worker; no extra summarization call. |
| Disabled/planned feature becomes a marketing promise | Explicit pending inventory; verified visible evidence required for enabled catalogue. |

Capture sweep (run only on the owned server with the protected demo configuration):

```bash
/usr/local/lib/hermes-agent/venv/bin/python - <<'PY'
from dotenv import dotenv_values
import os
os.environ.update(dotenv_values('/etc/smartmeet-marketing/agent.env'))
os.execvp('node', ['node', 'ops/verify-captures.mjs'])
PY
```

This writes a machine-readable capture-verification.json and per-feature screenshots/evidence under AGENT_STATE_DIR. No real provider meetings, synthetic invitations or customer emails are sent by this sweep. Production static assets are read over HTTPS; read requests may include fonts/assets. This is not a network-isolated simulation of all providers.

The checks validate operation and bounds, not revenue uplift. Sales performance needs campaign/conversion measurement after humans publish.

## Observed results, 24 October 2026

- 15 Python tests and 2 Chromium policy/privacy tests pass.
- 27/27 deployed-UI capture workflows pass; machine-readable result: capture-verification.json.
- Python compile checks, Node syntax checks and systemd unit/calendar validation pass.
- Free-model writer/reviewer exercised with real dedicated-demo evidence; inaccurate preview/offline claims rejected during evaluation.
- First operational example accepted by Resend for both recipients; provider acceptance is not an inbox-delivery guarantee.
- Explicit User-Agent fixes the provider's HTTP 403/1010 rejection of Python's default user agent; transport regression test passes. Recovery used the same provider idempotency key.
- Fresh review identified pre-send retry, hidden evidence and duplicate-on-retry defects; each now has a passing regression test.
- Existing SmartMeet frontend, meeting APIs, media services and shared Hermes gateway were not redeployed or restarted.
- Follow-up Resend read reports `delivered` with both requested recipients.
- An authenticated scheduling capture also passes under the deployed unit's strict filesystem/private-temporary-directory sandbox. Existing sent-slot service execution exits successfully without resending.

## Scheduled-run audit, 24 October 2026

The 21:00 IST timer triggered on time, but both free-model attempts failed before delivery (malformed review output and a provider connection timeout). No email was sent for that scheduled run. Added strict complete-JSON-fence parsing, word-number timing-claim rejection, per-attempt stage/detail diagnostics, and bounded systemd retries every 15 minutes (three starts per two-hour window). All 17 Python and 2 Chromium tests pass; unit verification passes. Live recovery is recorded separately after checking delivery.

Live recovery result: the missed 21:00 IST slot was generated, reviewed and sent through the actual sandboxed service at 22:15:49 IST. Resend reports `delivered` for both requested recipients. The earlier example also remains `delivered`. Service result is success/exit 0, timer is enabled/active, next trigger is 00:00 IST on 25 October. Automatic retry was observed queued after a failed recovery evaluation; the final recovery was started manually to verify the changes without waiting another 15 minutes. This confirms delivery and the schedule configuration, not an uninterrupted history of three-hour deliveries. Free-provider failures can still delay or withhold drafts after retries.

Final audit checks: 18 Python tests plus 2 Chromium tests pass. Review feedback now reaches the next writer attempt, preventing repeated invented customer scenarios or outcome guarantees.

## Broader editorial content — 26 October 2026

The five-pillar calendar persists its brief per slot. Text-only runs use verified catalog claims and omit attachments, even if a stale screenshot is present. Demos and legacy cached drafts still require a screenshot for delivery. Tests cover preview promotion, failed-generation retries, matching writer/reviewer briefs, required demo attachments, calendar rotation and unchanged delivery safeguards. Preview runs now count in feature rotation.

Real previews run in `/var/lib/smartmeet-marketing/editorial-preview-20261026`, separate from scheduled delivery state, without sending mail. The first practical-advice preview passed on its second attempt. The initial modern-collaboration preview was withheld after malformed free-model reviews; this prompted clarification that only selected capability claims need checking, and stronger direction to lead with a human collaboration principle. Review success is not a guarantee of editorial quality.

Live model evaluation also exposed unsupported audience-prevalence wording. A regression test first failed on `many teams`, `most founders` and `team leads often`; the deterministic validator now rejects those forms and the writer receives explicit conditional-framing guidance. The updated suite passes 25 Python checks plus 2 browser checks.

Final real-preview result: both practical-advice and modern-collaboration drafts reached `preview` with `approved: true` and no unsupported claims. Published snapshots are in `examples/editorial/`. Neither draft was emailed. The broader collaboration draft benefits from human copy editing (its benefit phrase is a sentence fragment); factual approval is not a style guarantee. The deployed timer remains active and executes this checkout on its existing cadence.
