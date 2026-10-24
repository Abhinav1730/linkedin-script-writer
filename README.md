# SmartMeet LinkedIn marketing agent

An independent server agent that captures SmartMeet UI, writes sales-focused LinkedIn drafts using **Nous Hermes + OpenRouter free models**, reviews the claims and emails the draft with its screenshot to:

- rahuljalan23.rj@gmail.com
- abhinav.saxena1730@gmail.com

Posting is manual. There is no LinkedIn token, browser login or publishing endpoint.

## How it works

The IST timer runs at 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00 and 21:00. SQLite selects the least-recently attempted enabled feature. Playwright opens only allowlisted pages with the dedicated ordinary demo account, or uses labelled synthetic fixtures in the actual deployed frontend for meeting/recap/Canvas demonstrations. It does not start real meetings, invite customers or call meeting providers.

Only visible, redacted UI evidence and reviewed capability claims go to Hermes. Hermes has no browser, shell, mail tools, memory, shared identity files or mail credentials. The writer returns a strict JSON schema. Exact approved feature claims are inserted into the draft; a separate tool-free Hermes invocation checks the entire draft. Deterministic checks reject unsupported numbers, guarantees, offline claims, external links and malformed content. Screenshots are attached by the orchestrator, not selected by the model.

Both configured model IDs must be `openrouter/free` or end in `:free`. Failed/invalid output gets at most one additional writer/reviewer attempt, entirely on free models. A failed screenshot, invalid draft or failed factual review withholds email. No paid fallback. See [coverage](docs/coverage.md) for verified versus pending workflows. An automated reviewer reduces errors; humans still review every draft before posting.

A process lock and durable slot key prevent concurrent/duplicate delivery. `sending`, `sent` and `delivery_unknown` slots cannot automatically resend. Resend also receives a stable idempotency key. An interrupted `reserved` slot requires inspection. Definite pre-send `failed` slots can retry. Preview drafts can be promoted without regeneration. The duplicate-hook check also runs when reusing an approved draft.

## Setup

Requires Linux, Python 3.12+, Node 22+, installed Hermes and Chromium. This server uses Hermes at `/usr/local/lib/hermes-agent`, with Python `/usr/local/lib/hermes-agent/venv/bin/python`; tested Hermes revision `c86197e60798801f62986e4e59460b1272d0c687`. Follow Hermes's shipped `website/docs/guides/python-library.md` for another server; its supported setup is a Git checkout plus `uv sync`, not a PyPI package.

```bash
npm ci --ignore-scripts
npx playwright install chromium
install -d -m 700 /etc/smartmeet-marketing /var/lib/smartmeet-marketing/runtime /var/lib/smartmeet-marketing/hermes
install -m 600 .env.example /etc/smartmeet-marketing/agent.env
```

Fill the protected file with a dedicated OpenRouter key, Resend key, verified sender and random demo password. Values are JSON strings, loaded without shell evaluation. Never commit this file. On this server the demo account has already been provisioned. `python3 ops/provision-demo.py` creates/verifies only that ordinary identity through the existing localhost API; it does not confer any admin/organisation/Canvas grant. The checked-in Canvas/meeting demonstrations use synthetic identities and fixtures, not forged production grants.

```bash
npm test
# Capture verification needs protected demo credentials; use the Python environment loader,
# then node ops/verify-captures.mjs (see docs/verification.md).
./ops/run.sh                       # preview current three-hour slot
./ops/run.sh --send                # deliver approved current slot
```

Install only this new service/timer; no existing SmartMeet service restart or frontend deployment is needed:

```bash
install -m 644 ops/smartmeet-marketing.service ops/smartmeet-marketing.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now smartmeet-marketing.timer
systemctl list-timers smartmeet-marketing.timer
```

Paths in the unit/launcher match `/root/linkedin-script-writer`; adjust those for another checkout. The systemd sandbox writes only `/var/lib/smartmeet-marketing`, uses a private temporary directory, and reads the protected secret file. The deployed timer is independent of the shared Hermes gateway/cron and all meeting processes.

## Operations

- `journalctl -u smartmeet-marketing.service -n 30 --no-pager`
- Inspect protected runtime `state.db`, each slot's `attempts.json`, `evidence.json`, `candidate.json`, `review.json`, `draft.txt`, `screenshot.png` and `delivery.json`.
- A delivery ID means provider acceptance, not proof of inbox delivery. Check Resend for delivery/bounce status.
- To retry a definite pre-send failure: `./ops/run.sh --send --slot SLOT`. Never create a new slot just to bypass uncertain delivery.
- For `reserved`/`sending`/`delivery_unknown`, inspect the local receipt and Resend history first. Do not edit state to resend unless delivery has been reconciled.
- Stop scheduling with `systemctl disable --now smartmeet-marketing.timer`; this leaves running meeting services untouched.
- Keys remain external, and deployment rollback is a Git checkout plus restoration of the new service files. Preserve private SQLite/evidence across releases.

Free-provider availability, quota and rate limits vary. Runs can fail closed; no paid-model fallback or sales outcome is promised. The cadence is eight drafting opportunities daily, not eight automatic LinkedIn posts. [OpenRouter free routing](https://openrouter.ai/docs/guides/routing/routers/free-router) and [Hermes Python library](https://hermes-agent.nousresearch.com/docs/guides/python-library) describe the upstream components.
