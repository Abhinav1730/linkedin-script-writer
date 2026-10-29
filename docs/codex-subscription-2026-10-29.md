# Marketing inference through Codex subscription, 29 October 2026

The marketing writer and independent reviewer now use the existing Codex CLI ChatGPT sign-in. The approach follows SmartMeet's established `canvas-workers/src/runtimes/codex.ts` adapter: start a stdio app-server, require `account/read.account.type=chatgpt`, select the OpenAI model provider, start an ephemeral read-only thread with no tools, and submit a bounded turn with a strict output schema.

The currently accepted CLI is `codex-cli 0.164.0`. The inherited subscription model is `gpt-6-luna`. A model override can be supplied separately for writer/reviewer, but there is no API-key or OpenRouter route. Native subprocess environments omit OpenAI, Codex, OpenRouter, mail and demo-account keys. All configured MCP servers and the applicable tool/app/plugin/memory features are disabled; unexpected tool items or server approval/tool requests fail the turn. No authentication material is copied or extracted. The service reuses `/root/.codex`, with write access for the CLI's supported token refresh and native state.

`src/prompts.py` preserves the existing writing/review instructions. `src/model_json.py` preserves strict JSON parsing. The previous Hermes/OpenRouter worker is removed. Invalid output or rejected review may retry once on Codex. Subscription exhaustion fails the job under the existing scheduler retry limits; it does not enable API fallback.

The editorial schedule, catalog, screenshot policy, recipients, human posting requirement, bounded attempts and durable no-duplicate/uncertain-email rules are retained. API-credit configuration from the separate SmartMeet provider-router task is not required for these subscription turns.

## Acceptance

- All 28 Python pipeline/transport tests and two browser-policy tests pass. Added checks cover omitted API/mail credentials, rejection of API-key accounts before any turn, forbidden tools/approval calls, and separate writer/reviewer output schemas.
- A real Codex reviewer turn reports `provider=codex-subscription`, `auth=chatgpt`, model `gpt-6-luna`, and measured token usage. The controlled draft is approved.
- A complete real writer/reviewer preview also passes the deterministic checks and independent review using the subscription. Writer: 5,936 input / 127 output tokens. Reviewer: 5,913 input / 64 output tokens. No email is sent. Evidence and isolated preview state are under `/var/lib/smartmeet-marketing/verification/codex-switch-20261029`.
- The production switch must use only an idle marketing-service cutover, retain the delivery database and protected rollback copies, and verify a fresh no-send preview under the service sandbox. Other SmartMeet services and the timer schedule are not deployment targets.

## Runtime and rollback

Tracked source is staged as an immutable release under `/srv/smartmeet-marketing/releases/`, selected through `/srv/smartmeet-marketing/current`. Only the marketing unit and its protected `/etc/smartmeet-marketing/agent.env` change. Remove obsolete marketing `OPENROUTER_*` and `HERMES_*` settings; preserve mail/demo settings and `AGENT_STATE_DIR`. Set the existing Codex binary/home paths and leave model overrides empty to use the accepted subscription default.

Successful inference records only provider, auth mode, version, model, stage and usage in `runtime/codex-calls.jsonl`. Auth failure, changed CLI version, malformed output, tool activity and uncertain native outcomes withhold email. Never bypass the durable slot states to resend an uncertain delivery.

Rollback restores the previous marketing unit and protected configuration copy and selects its previous source. Keep all production delivery state. Do not roll back or restart meeting/media, Canvas, API, admin or unrelated services for this change.
