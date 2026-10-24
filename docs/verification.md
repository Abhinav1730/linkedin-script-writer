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
