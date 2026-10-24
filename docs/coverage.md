# Feature coverage and evidence boundaries

The catalogue scripts a rotation of customer-facing SmartMeet capabilities. Each selected feature requires a fresh screenshot and expected visible evidence before writing. Recap, live meeting and Canvas demonstrations use the deployed production UI with synthetic fixtures, labelled DEMO. These show the interface, not a customer endorsement or measured production outcome. Account screenshots use only the dedicated marketing-demo@smartmeet.invalid account.

Covered: instant setup; meeting scheduling; dashboard; integrations and explicit action approval; history filtering; Canvas sign-in; microphone/camera/chat/screen-sharing/participant controls; visual reactions; summary email preferences; detailed reports; AI recap sections; tasks by person; screen observations; transcript evidence; tool-action sign-in; avatars; admission choices; device checks; recording disclosure; invite controls; camera backgrounds; Canvas projects/private and shared spaces/briefs/files; booking entry.

Additional demos require their own verified workflows before enabling claims:
- Organisation agents: separate enrolled demo organisation and source-local identity/grants; ordinary demo login is not authority.
- Browser extension: staged supported browser with the extension installed and verified receiver; no automatic Chrome Store/publication claims.
- Private games: current deployed navigation must expose the game launcher; do not market a hidden or unavailable entry point.
- Advanced Canvas execution, research, agents and professional tools: verify individual deployed capabilities before making execution/outcome claims. A tab or app listing is not proof that an execution backend is enabled.

To add coverage, extend config/features.json with exact implemented claims, deterministic UI steps and evidence terms, then run the complete capture sweep. Never use model-invented navigation or credentials. Review scope against current release metadata as SmartMeet evolves. All-feature coverage is a continuing inventory, not a claim that every planned feature is available.
