# Repository and dependency routing

Public workflow: https://github.com/CopernicusP/editorial-playbook

Resolve a supplied checkout or snapshot first. Otherwise read the public repository and record its current commit before selecting files. Do not silently mix versions. A standalone installation of this skill reads the repository documents; it does not bundle them or provide offline access to them.

| Need | Repository path |
| --- | --- |
| Start a run | `AGENTS.md`, `profiles/example.json`, `templates/episode-brief.md` |
| Input routing and production | `docs/WORKFLOW.md` |
| Research from a topic | `templates/research-brief.md`, `templates/claim-ledger.md` |
| Article request | `templates/article-request.md` |
| Review, repair and handoff | `docs/QUALITY.md`, `templates/editor-feedback.md` |
| Requested audio or video | `docs/MEDIA.md` |

Read only applicable documents. A private organization profile overrides example selections, not the user's current instructions. Keep private requirements and source packets in the authorized run location.

## Writing core

Use [Evidence to Article](https://github.com/CopernicusP/evidence-to-article), version **0.2.0**, commit **ba0f2d04d3b64a67e9118273444dc19bbd8f0ccc**. Read the [pinned core skill](https://github.com/CopernicusP/evidence-to-article/blob/ba0f2d04d3b64a67e9118273444dc19bbd8f0ccc/skills/evidence-to-article/SKILL.md) and applicable references. Relative links resolve inside that same commit.

Use the core's `references/authorial-voice.md`, `references/editorial-decisions.md` and relevant `references/channels.md` sections for writing. Before using its export/audit helpers, read `references/manifest-contract.md`. The helpers live in the core and do not fetch this wrapper or enforce every profile field. Use them only with real sources and review records. The v0.2.0 checker expects TXT and HTML companions for each canonical article; these can remain internal verification exports when the requested delivery is DOCX only.

Upgrade the dependency explicitly after reviewing changes and trying representative inputs. General writing improvements belong in the core; channel choices and production routing belong here; organization-specific information belongs in a separate private profile.
