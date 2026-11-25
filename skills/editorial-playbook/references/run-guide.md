# Prepare, execute and accept a run

## 1. Select scope

Use the bundled `presets/bilingual-finance.json` for a finance explanation package. All its targets are editable: research approximately 15–20 rendered pages, English blog 2–3 body pages, Chinese article 2,000–3,000 body Han characters, and optional English podcast approximately ten minutes including any permitted intro/outro. These are operating suggestions, not a company's policy. Use the current brief to choose the space the explanation needs. Keep a key comparison or an extra step that lets the reader follow a mechanism. Meet a strict limit by cutting lower-priority material. Record actual counts and reasons for deviations.

- `articles`: English research DOCX, English blog DOCX, Chinese TXT/HTML, claim ledger.
- `podcast`: articles plus English recording script DOCX, MP3 and the actual audio transcript TXT.
- `video`: podcast plus timecoded storyboard TXT, permitted visual assets ZIP and MP4.

Use the user's requested package. For a custom selection or strict target, provide a compatible private preset with `--preset`; do not quietly drop required files from the existing package. An existing research report can be reused if it is the actual reviewed input and satisfies the selected delivery scope.

## 2. Prepare

From this skill's directory, run:

```bash
python3 scripts/prepare_run.py --run-dir /path/to/new-private-run --topic "Reader question" --input-mode research --cutoff 2026-11-17 --package articles
```

Use the real cutoff, topic and input route (`topic`, `research` or `draft`). `--engine-source /path/to/core-repository --offline` uses an existing source copy; it still verifies the bundled hashes. A public connector can supply the locked files into repository-relative paths when direct downloads are unavailable. Do not call network access verified when only an offline cache was used.

Use `--capabilities /path/to/capabilities.json` to pass observations such as `{"source_access":{"status":"available","evidence":"The requested source was opened in this session."}}`. Allowed status values are available, unavailable and unknown. Do not invent access evidence. The loader checks Python and core bytes; external capabilities are declared observations, not machine-certified availability. The generated preflight distinguishes them.

The run contains a preset snapshot, `RUN.md`, empty article-audit manifest, delivery inventory and preflight results. Nothing in an empty inventory is approved. The directory must be new or empty; an existing run is not overwritten.

### Carry a commission through revisions

Use `--revision-plan /path/to/plan.json` whenever the assignment includes earlier agreed changes or a comparison whose endpoints must survive subsequent edits. Choose the input route from the actual materials. A filename or round label cannot establish what was requested or approved.

Before writing, reconstruct the commission, each accepted fix, and the latest instructions. Give each requirement an ID, source location and canonical article ID in the pinned core's `rounds` format (see `references/manifest-contract.md` in the core). A later explicit scope or length replaces an earlier instruction only for the affected output. Name the earlier requirement in `supersedes` and cite the reason. If the commission compares two sources, identify both and the question their comparison must answer. Use `--preset` to select the deliverables actually commissioned.

If an earlier checked plan exists, keep its exact bytes at a run-relative archive path. Bind its path and digest in `previous_plan`, keep its rounds intact and append the new round. A `prior_fix` can identify an archived UTF-8 draft by path, digest and exact quotation. Stage these records at their declared paths in the prepared run. If no earlier plan exists, reconstruct the commission from identifiable instructions and accepted edits, and record any unavailable history.

Preparation copies the original plan bytes to `revision-plan.json` and binds its digest in `run.json` and `core-manifest.json`. Populate `cumulative_revision.checks` with current evidence after the edits. For each active requirement quote the final passage and explain how it satisfies the commission or preserves the accepted repair. Give the continuity specialist and the fresh final reader the agreed plan. Use the core's plan and checks digests to bind their decisions. If scope changes again, prepare a new run from a revised plan and retain the earlier records.

## 3. Execute the verified core

Read `RUN.md`, then `.engine/skills/evidence-to-article/SKILL.md` and its applicable references. Research the question or verify supplied research; read raw sources, build the claim ledger, compose languages independently. Follow the criterion assignments, rechecks and fresh whole-article review in the core. Read its `references/editorial-decisions.md` and `references/manifest-contract.md`. Use the bundled preset's grounded personal Chinese voice, declarative headings, subtitle, source list and appropriate disclaimer. Keep authorship, dates, numerical meanings, conditions and uncertainty consistent across channels.

Use the actual core exporter for internal Markdown/TXT/HTML audit companions. Use `python3 -B` for any direct invocation of cached core scripts, so they do not add untracked bytecode to the verified dependency. A reader-facing plain TXT, document or publishing-editor HTML may use another renderer, but its `output_consistency` check must be bound to the audited canonical article. Inspect the actual document pages and publishing-editor preview. Include the disclaimer outside the body-count scope and report that counting choice.

If media is requested, select the actual allowed Google provider, preserve provenance and original audio, and check the finished spoken content. Keep the script separate from the transcript. Perform full listening; for video inspect the actual exported timeline and visual assets. Incomplete capabilities leave a specific task blocked, not falsely completed.

## 4. Record actual checks

Use schema 2 in `core-manifest.json`. Name the one integrating writer in `integrator_id`. For each article record its applicable `required_criteria` before dispatch. Include `readability`, `source_meaning` and `delivery`. Assess `number_relevance`, `reader_implications`, `reader_teachback`, `closing_synthesis` and `comment_closure`. When readers may lack assumed knowledge, assign `reader_teachback` to its own independent reviewer, including for a revision prompted by reader confusion. Give them the article and audience description alone for the first read, then record their unaided explanation and the exact step they could not reconstruct. Comment closure applies when feedback was supplied. For a scoped criterion that genuinely does not apply, explain why in that article's `inapplicable_criteria` object, keyed by criterion. Lack of a reviewer is an incomplete review, never a reason to exclude a criterion. Add any further independent tests the brief requires. Keep assignments consistent across the run. Once all specialists finish, the same fresh final reviewer reads all integrated articles and binds the read to each article hash. Use the verified core contract for fields and timing.

`delivery.json` lists each required role. Complete items require the real path, author ID, SHA-256, relevant canonical article ID and all preset check records. A check contains kind, status, reviewer ID and actual reviewer type (agent, human or tool), reviewed_at with timezone, current artifact_sha256 and a concrete evidence note. Use pass only for a performed check; otherwise fail or not_run.

For `output_consistency`, bind `related_hashes.canonical` to the audited article. Bind transcript alignment, storyboard timing and video sync to `related_hashes.audio_mp3` from the actual final audio. A changed file invalidates its hash-bound checks. Record measured pages on document_render checks and seconds on media_duration checks; Chinese body counts are obtained from the core. `audio_mp3.provider` must match the selected preset's permitted product identifiers.

Full check examples and field details are in the public [delivery contract](https://github.com/CopernicusP/editorial-playbook/blob/main/docs/DELIVERY-CONTRACT.md). The script validates the record; it cannot independently establish that a person or agent truthfully performed the claimed work. Never fabricate identities or evidence to close a checklist.

## 5. Accept and hand off

```bash
python3 scripts/check_delivery.py --run-dir /path/to/private-run --report /path/to/private-run/acceptance-V1.json
```

The checker verifies the locked dependency, runs its article checker anew, and checks required outputs, formats, hashes, measurements and current attestations. It does not call an LLM, perform source research, listen to audio, send messages or publish. Use a fresh report filename on each run; existing report files are not overwritten.

For a cumulative package, the checker requires the prepared plan and invokes the core in cumulative mode. An independent handoff can also supply `--require-cumulative` or `--expected-plan-sha256 <digest-from-preparation>`. When a current plan assigns a body-page range to a delivered document, inspect its final PDF. Record the occupied fraction of the usable body area per physical page, with zero for references. In a DOCX item's `document_render` check include `render_sha256` for the inspected PDF. The checker compares the plan's role, actual delivered bytes, render digest and physical page count using `pdfinfo` or `pypdf`. It reports the sum of the fractions; the reviewer supplies the body-area observations.

Only `ready_for_handoff` exits with code 0. Other outcomes name incomplete work, blocked tasks, changes required or a required approval still pending. Read warnings and reviewer findings even when the record is complete. Human/organization approval is configured only when it actually applies. A successful record check is not factual certification or evidence of publication.

Give the user the real requested files, each file's purpose and specific remaining issues. Keep source and review records in the authorized private run folder.
