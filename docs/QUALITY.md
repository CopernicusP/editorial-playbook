# Quality review and handoff

The purpose of review is to locate and repair failures a reader would encounter. A checklist completion, an AI-detector score or a fluent paragraph is not evidence that an article is accurate or useful.

Use the pinned core's [review and repair workflow](https://github.com/CopernicusP/evidence-to-article/blob/ba0f2d04d3b64a67e9118273444dc19bbd8f0ccc/skills/evidence-to-article/SKILL.md). This page specifies how the playbook coordinates its review records and delivery.

## Separate the responsibilities

The coordinator selects the supported angle, assigns section jobs, integrates findings and makes actual revisions. Use fresh reviewers separate from the writer when available. Give each the brief, current artifacts and source locations without an expected approval.

| Review lane | Required work | Useful finding |
| --- | --- | --- |
| Readability | Read each requested language as a complete article; reconstruct the argument from the lead and headings, then inspect transitions, explanation and voice | A quoted passage, the reader difficulty it creates, and a concrete repair |
| Source and meaning | Open the evidence behind material claims; check measures, dates, actors, attribution, conditions and cross-language consistency | The claim, source locator, supported scope and correction required |
| Overall and delivery | Reconcile revisions, scope, lengths, versions, exports and requested media; inspect the actual rendered or played artifact as applicable | The affected file, observed mismatch or missing check, and its delivery consequence |

Different lanes are responsibilities, not fictional people. If fresh agents are unavailable, record separate passes under the real reviewer identity and identify the limited independence. Do not invent reviewers or claim the core's independent-review requirement passed.

## Record findings against actual files

Use the [feedback record](../templates/editor-feedback.md). Each review names the artifact and its actual SHA-256, reviewer identity, lane, decision, findings and unresolved items. Keep the observations concrete: “the second heading repeats the conclusion without advancing it” is actionable; “make it more human” is not a completed diagnosis.

After edits, affected lanes review changed substance and its consequences. Other lanes inspect the difference before renewing a decision. No approval carries over by merely replacing an old hash. Regenerate derived files and preserve superseded decisions separately from the active review record.

After two unsuccessful repairs of the same issue, change the approach or disclose the precise unresolved issue and its effect. Do not repeat cosmetic rewrites and report a new success each time.

## Verify the forms readers will receive

- Count length using the recorded convention. Report actual counts; do not pad a draft with repeated conclusions to hit a target.
- Inspect document rendering when page count or layout matters. A successful file write does not show that its pages are readable.
- Compare canonical text with requested exports. Check encoding, headings, links, source notes and visible text. A browser HTML check is not a publishing-platform preview.
- Use the [media checks](MEDIA.md) for actual audio or video. Do not report a listening or playback check that did not occur.
- Check timeliness against the run's cutoff and source access. A source's event date, publication date and latest-status date can differ.

The core's [deterministic checker](https://github.com/CopernicusP/evidence-to-article/blob/ba0f2d04d3b64a67e9118273444dc19bbd8f0ccc/skills/evidence-to-article/references/manifest-contract.md) checks declared records, hashes, lengths and export consistency. Report its result separately from the reviewers' semantic findings. It cannot determine that a source truly supports a claim or that the prose reads well.

## Reduce repeated editing through evidence

When an editor revises a passage, capture what changed and why. Promote a recurring preference into a scoped rule only when the evidence supports that generalization: specify the language, channel, audience and example where it applies. Keep a one-off factual correction in the current run. Do not blend unrelated authors' preferences into a shared voice.

Assess a workflow change on comparable tasks. Record major factual repairs, structural revisions, passages the editor rewrote, elapsed editing time when measured, and direct reader feedback when collected. A favorable response to one draft is useful feedback, not proof of broad improvement or time saved. Public examples should be synthetic or explicitly cleared for public use.

## State delivery readiness accurately

Use separate fields for drafting, agent review, any required human/organization review, media checks and publication. Complete routine editorial judgments within the authorized task; do not return a generic requirement for someone to polish every paragraph. Escalate only a consequential unresolved purpose, indispensable missing access/evidence or an applicable approval that is genuinely absent.

The handoff should name the requested deliverables, versions, source cutoff and actual completed checks. State any remaining issue in terms of its effect on use. Sending, publishing and changing access require the user's applicable authorization and are not implied by a quality pass.
