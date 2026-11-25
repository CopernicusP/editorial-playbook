# Repository and dependency routing

Public workflow: https://github.com/CopernicusP/editorial-playbook

Resolve a supplied checkout or snapshot first. Record the playbook version and actual source used. The installable skill bundles its runtime scripts, run guide, finance preset and engine lock. It can prepare from a verified offline source copy. The optional longer guides and templates remain in the public repository; record their actual access rather than assuming they were read.

| Need | Repository path |
| --- | --- |
| Prepare a finance run | `skills/editorial-playbook/references/run-guide.md`, `skills/editorial-playbook/references/presets/bilingual-finance.json` |
| Understand acceptance | `docs/DELIVERY-CONTRACT.md` |
| General planning | `AGENTS.md`, `templates/episode-brief.md` |
| Input routing and production | `docs/WORKFLOW.md` |
| Research from a topic | `templates/research-brief.md`, `templates/claim-ledger.md` |
| Article request | `templates/article-request.md` |
| Review, repair and handoff | `docs/QUALITY.md`, `templates/editor-feedback.md` |
| Requested audio or video | `docs/MEDIA.md` |

Read only applicable documents. `profiles/example.json` remains a legacy descriptive profile and is not accepted as a runtime preset. A compatible private preset can select real organization requirements; keep it and its source packets in the authorized run location. Current user instructions take precedence.

## Writing core

Use [Evidence to Article](https://github.com/CopernicusP/evidence-to-article), version **0.3.0**, commit **064f31c978860ecbb8c9c2162900e82568946c7e**. `references/engine-lock.json` selects exact file hashes. Preparation loads those files into the run; acceptance verifies them again before executing the core checker. Read the verified local skill and applicable references, or the [pinned public skill](https://github.com/CopernicusP/evidence-to-article/blob/064f31c978860ecbb8c9c2162900e82568946c7e/skills/evidence-to-article/SKILL.md) for a clearly labeled no-code fallback.

Use the core's `references/authorial-voice.md`, `references/editorial-decisions.md` and relevant `references/channels.md` sections for writing. Follow the criterion-by-criterion dispatch, then read `references/manifest-contract.md` for the schema-2 specialist and whole-article review records. Use the same pinned references in the no-code route and record actual capabilities and versions. The v0.3.0 core checker expects TXT and HTML companions for each canonical article; keep those internal if they are not requested deliverables. The wrapper's separate acceptance checker applies the selected package requirements without pretending the core can inspect Word layout, judge prose or hear media. Neither script grants publication approval.

Upgrade the dependency explicitly after reviewing changes and trying representative inputs. General writing improvements belong in the core; channel choices and production routing belong here; organization-specific information belongs in a separate private profile.
