# Remaining work

- Review and refine audience, brand voice and CTA from actual marketing feedback; defaults are English, business teams/founders and smartmeet.org.
- Track sales/conversion outcomes manually initially; no evidence yet that these drafts improve conversion.
- Expand coverage only with verified workflows listed in docs/coverage.md; never imply planned/disabled capabilities work.
- Free provider availability and limits can prevent a run even after the bounded 15-minute automatic retries. Failed content is withheld, not replaced by a paid model or unverified post. Monitor systemd journal and private attempts.json.
- Delivery receipt means mail-provider acceptance, not guaranteed inbox delivery; investigate bounces in Resend.
- Scope retention/backup for private evidence and SQLite as usage grows; keep any demo credentials, session state and provider keys outside Git.

- Collect feedback on the five editorial themes; current collaboration posts are perspectives, not live trend research. Illustrative graphics are not generated.
- Human copy editing remains necessary: the approved collaboration preview contains a benefit sentence fragment; automated factual review does not guarantee polished prose.
# Codex subscription switch, 29 October 2026

- [x] Writer/reviewer adapter, subscription-authentication/tool guards, current CLI acceptance, existing pipeline tests and real no-send preview.
- [ ] Idle marketing-only rollout, fresh service-sandbox acceptance, removal of obsolete provider settings, and confirmation of the existing timer.
- [ ] Reaccept future Codex CLI versions before changing the pinned version; monitor subscription quota through ordinary job status.
