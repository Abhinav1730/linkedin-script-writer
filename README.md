# SmartMeet LinkedIn marketing agent

An independent server agent that captures SmartMeet UI, writes sales-focused LinkedIn drafts using **the existing signed-in Codex subscription**, reviews the claims and emails the draft (with a screenshot for feature demos) to:

- rahuljalan23.rj@gmail.com
- abhinav.saxena1730@gmail.com
- vig6604@gmail.com

Posting is manual. There is no LinkedIn token, browser login or publishing endpoint.

## How it works

The IST timer runs at 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00 and 21:00. The editorial calendar rotates user value, practical advice, modern collaboration, audience use cases and feature demonstrations across slots. SQLite independently selects the least-recently attempted enabled feature. Each slot retains its editorial brief on retries. Playwright opens only allowlisted pages with the dedicated ordinary demo account, or uses labelled synthetic fixtures in the actual deployed frontend for meeting/recap/Canvas demonstrations. It does not start real meetings, invite customers or call meeting providers.

Feature demonstrations require fresh, visible, redacted UI evidence. Other themes use the source-owned verified capability catalog and send text-only emails; an old screenshot is never attached to those drafts. Modern collaboration posts offer perspectives and hypothetical scenarios, without unsupported current trend claims. Reviewed capability claims and the editorial brief go to Codex in a fresh ephemeral, read-only, tool-free app-server thread. The worker verifies ChatGPT subscription authentication and never receives API, mail or demo-account credentials. The writer returns a strict JSON schema. Exact approved feature claims are inserted into the draft; a separate tool-free Hermes invocation checks the entire draft. Deterministic checks reject unsupported numbers, guarantees, offline claims, external links and malformed content. Screenshots are attached by the orchestrator, not selected by the model.

Writer and reviewer use the existing Codex subscription model by default. Optional `MARKETING_CODEX_MODEL` and `MARKETING_CODEX_REVIEW_MODEL` settings select Codex model IDs. Failed/invalid output gets at most one additional writer/reviewer attempt, entirely on Codex. A failed screenshot, invalid draft or failed factual review withholds email. The service automatically retries pre-send failures after 15 minutes, up to two additional starts within two hours. Unknown or completed delivery remains blocked from automatic resending. No OpenRouter or API-key fallback. See [coverage](docs/coverage.md) for verified versus pending workflows. An automated reviewer reduces errors; humans still review every draft before posting.

A process lock and durable slot key prevent concurrent/duplicate delivery. `sending`, `sent` and `delivery_unknown` slots cannot automatically resend. Resend also receives a stable idempotency key. An interrupted `reserved` slot requires inspection. Definite pre-send `failed` slots can retry. Preview drafts can be promoted without regeneration. The duplicate-hook check also runs when reusing an approved draft.

## Setup

Requires Linux, Python 3.12+, Node 22+, Chromium and Codex CLI `0.164.0`. This server already has Codex at `/root/.local/bin/codex`, signed in with ChatGPT. The adapter reuses that supported sign-in with `CODEX_HOME=/root/.codex`, checks `account/read` for account type `chatgpt`, and disables tools/MCP, web search, local project instructions and memory. It never converts subscription tokens into API keys. A CLI version change requires acceptance before scheduled use.
```bash
npm ci --ignore-scripts
npx playwright install chromium
install -d -m 700 /etc/smartmeet-marketing /var/lib/smartmeet-marketing/runtime
install -m 600 .env.example /etc/smartmeet-marketing/agent.env
```

Fill the protected file with the existing Codex binary/home paths, Resend key, verified sender and random demo password. No OpenRouter or OpenAI API key is needed for inference. Values are JSON strings, loaded without shell evaluation. Never commit this file. On this server the demo account has already been provisioned. `python3 ops/provision-demo.py` creates/verifies only that ordinary identity through the existing localhost API; it does not confer any admin/organisation/Canvas grant. The checked-in Canvas/meeting demonstrations use synthetic identities and fixtures, not forged production grants.

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

The unit reads the immutable release selected by `/srv/smartmeet-marketing/current`. Stage tracked source there, with the installed Playwright dependency directory available as `node_modules`, before installing the unit. The launcher resolves its own source directory. The systemd sandbox writes marketing artifacts under `/var/lib/smartmeet-marketing` and permits the existing `/root/.codex` store to handle subscription token refresh and native session state. It uses a private temporary directory and reads the protected configuration file. The deployed timer is independent of other model gateways/cron and all meeting processes.

## Operations

- `journalctl -u smartmeet-marketing.service -n 30 --no-pager`
- Inspect protected runtime `state.db`, each slot's `attempts.json`, `evidence.json`, `candidate.json`, `review.json`, `draft.txt`, `screenshot.png` and `delivery.json`.
- A delivery ID means provider acceptance, not proof of inbox delivery. Check Resend for delivery/bounce status.
- To retry a definite pre-send failure: `./ops/run.sh --send --slot SLOT`. Never create a new slot just to bypass uncertain delivery.
- For `reserved`/`sending`/`delivery_unknown`, inspect the local receipt and Resend history first. Do not edit state to resend unless delivery has been reconciled.
- Stop scheduling with `systemctl disable --now smartmeet-marketing.timer`; this leaves running meeting services untouched.
- Keys remain external, and deployment rollback restores the previous source pointer, unit and protected config backup. Preserve private SQLite/evidence across releases.

Codex subscription usage limits still apply. Exhaustion or failed sign-in withholds the draft and uses only the existing bounded/scheduled retries; it never falls back to a paid API or OpenRouter. The cadence is eight drafting opportunities daily, not eight automatic LinkedIn posts. Successful native calls record provider, authentication mode, actual model and token counts in protected `runtime/codex-calls.jsonl`, without prompts or credentials. See [the subscription switch and live acceptance](docs/codex-subscription-2026-10-29.md).
