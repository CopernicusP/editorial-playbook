---
name: editorial-playbook
description: Run a research-to-publication workflow from a topic or an existing research packet. Use for Chinese explanatory articles, English blogs and requested podcast or video deliverables, with shared evidence, independent review of each applicable editorial criterion, and explicit production status. Uses Evidence to Article as the writing core and accepts organization profiles supplied for each run.
---

# Editorial Playbook

Version: 0.3.0. Use the bundled preparation and acceptance tools to coordinate research, bilingual writing and requested media. Use Evidence to Article v0.3.0 as the writing and article-audit engine. Read [references/run-guide.md](references/run-guide.md) first and [references/routing.md](references/routing.md) for dependency and repository details. The tools prepare and inspect a run; the host agent performs research, writing, review and media production.

## Establish one run

Read the user request, latest supplied material and current editorial feedback. Identify audience, central question, factual cutoff, requested channels, length and delivery location. Use an isolated authorized work folder. For the full bilingual finance workflow select the bundled [bilingual-finance preset](references/presets/bilingual-finance.json) and the articles, podcast or video package. Packages add media cumulatively. For other requirements use an explicit compatible preset. Keep the public legacy example profile as a writing suggestion only; it is not the runtime preset schema. Current task requirements take precedence: record deliberate changes in the selected preset before preparation. Do not load unrelated project memories or historical feedback as current requirements.

When Python execution is available, run `scripts/prepare_run.py` with the brief and selected package. It fetches or reads the exact core files selected by the bundled engine lock, verifies their hashes and creates a run brief, manifests and preflight record. Read the resulting `RUN.md` and verified core skill/references; downloading instructions alone does not execute them. Check the actual host tools and record evidence for available capabilities. Unknown or unavailable media capability must not prevent useful article work. The program cannot grant external access or create independent reviewers.

When code execution is unavailable, read the preset, pinned public core and relevant workflow documents directly. Complete supported work and clearly label the missing automated checks and capabilities. Record preparation, review and acceptance separately. Report any independent reviews actually performed, with their scope and version. Leave unperformed checks open. Do not silently replace the core with remembered instructions.

## Route the input

- For a topic, define the question, scope and evidence needed using the research brief, then conduct research and build the claim ledger. A research brief is not a research report. Record source access and unresolved gaps.
- For existing research, read it first, check its sources and cutoff, and investigate material gaps. Reuse sound research. A supplied report is an input to verification, not proof that every claim is true.
- For a draft revision, read the current text and accessible comments before editing. Capture each comment ID, original passage and requested change. Preserve approved material. Locate the final replacement and verify whether it answers the comment. Record retained wording, open items and access gaps with reasons.

## Write, review and repair

Read the workflow and quality guides. Delegate composition to the pinned core. Select a supported angle, give each section an explanatory purpose, and write Chinese and English independently from shared evidence. When grounded personal voice is selected, load the core authorial-voice reference; make analysis visible without inventing experience or increasing certainty.

Follow the core's criterion-by-criterion dispatch in `references/editorial-decisions.md`. Assign **one independent reviewer per applicable criterion**. Separate prose, source fidelity and delivery. Use distinct assignments for numerical evidence choice, consequences for the named reader, whether the ending answers the opening, and closure of supplied comments. Record the reason for a criterion outside scope. Give reviewers the brief, evidence and current artifacts without earlier verdicts.

One writer integrates the findings. Affected specialists recheck the revised passages in context and the other specialists inspect the changes before renewing their decisions on the current version. Once all specialists have completed their rechecks, one fresh reviewer, who neither wrote, integrated nor reviewed any part, reads the complete editorial work across all requested languages and returns a verdict. Keep each specialist on the same criterion throughout the run. An edit after this read reopens affected checks and the whole-article review. Record actual reviewer identity, type, criterion, artifact version/hash and outstanding findings. Identify agent judgments, direct human feedback and publication approval accurately. If independent review is unavailable, report the available work as a limited-review draft.

Resolve ordinary choices of angle, wording, section order and endings within the task. Ask only for a consequential missing purpose, indispensable evidence/access or genuinely required authorization that has not already been given. Record concrete unresolved issues rather than returning a generic request for human polish. Keep required human or organization approval separate from agent review.

## Produce requested formats

Lock canonical text before exports. Derive formats from it, inspect actual renders, and report real counts using the selected convention. The core TXT exporter retains Markdown syntax; use and verify a separate renderer if the destination needs clean plain text. A local HTML preview is not a publication-platform preview. Use V1/V2/Draft filenames and record review/publication status separately.

For audio or video, read the media guide. Verify the actual provider and source audio; distinguish the recording script from the transcript of the finished track. Check generated additions against the ledger. A completed script does not imply an MP3 exists. Do not silently substitute another provider. Record actual listening, duration, timeline and video inspection; leave unperformed checks unperformed.

Fill `core-manifest.json` from actual evidence and independent article reviews. Record each requested deliverable and its genuine checks in `delivery.json`; hashes bind article adaptations, transcripts and media to the versions checked. Run `scripts/check_delivery.py --run-dir <run>` after repairs. It freshly invokes the verified core checker and checks package files and required attestations. Its result does not independently prove that an attestation is true or that prose and media are good.

Deliver complete work and report unresolved requirements by role. Distinguish incomplete, blocked, changes_required, approval_pending and ready_for_handoff. A required publication approval remains separate; do not introduce one when it does not apply. Keep private run material outside the public repository. Sending messages, uploading non-public material or publishing needs applicable user authorization; the playbook itself grants none.
