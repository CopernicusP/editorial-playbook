# Delivery acceptance contract

The acceptance command checks files and records for one prepared run. It does not write the content, establish factual truth, prove a review occurred, or publish the package.

Run:

```bash
python3 skills/editorial-playbook/scripts/check_delivery.py \
  --run-dir /path/to/private-run \
  --report /path/to/private-run/acceptance-V1.json
```

The bundled dependency lock identifies the executable core. The checker verifies its bytes and invokes it freshly. A saved core-success report is not a substitute.

Use a new report filename for each saved audit; existing report files are not overwritten. Omitting `--report` prints the result without creating a report file.

## Keep two records

| Record | Contents |
| --- | --- |
| `core-manifest.json` | Canonical articles, their internal TXT/HTML companions, sources, exact claim occurrences, one independent specialist per applicable criterion and a subsequent fresh whole-article review |
| `delivery.json` | Every requested preset role, its delivered file, current status/hash, required checks and any applicable approval |

Follow the core's [manifest contract](https://github.com/CopernicusP/evidence-to-article/blob/064f31c978860ecbb8c9c2162900e82568946c7e/skills/evidence-to-article/references/manifest-contract.md). New packages require schema 2, including scoped criteria, current specialist approvals and the later whole-article review. See the [run guide](../skills/editorial-playbook/references/run-guide.md) for criterion IDs and applicability notes. Use the matching earlier playbook and lock to reproduce an archived run. Keep the core manifest directly in the run directory so its relative artifact paths use the same base. Article deliverables must identify the correct audited canonical article and language. Internal audit exports can remain separate from reader-facing files.

Factual packages require nonempty source and claim inventories. Empty inventories keep a package incomplete even where the underlying core reports only a coverage warning.

The generated `profile.json` is bound to the run by its hash. Required roles and checks come from that selected preset, not from whichever entries happen to be present in the delivery record. A missing required file cannot disappear by deleting its checklist row.

## Bundled roles and required checks

| Role | Format | Required checks |
| --- | --- | --- |
| `research_en` | DOCX | `source_review`, `document_render`, `format_review` |
| `blog_en` | DOCX; canonical language `en` | `document_render`, `output_consistency`, `format_review` |
| `article_zh_txt` | UTF-8 TXT; canonical language `zh` | `output_consistency`, `format_review` |
| `article_zh_html` | Static HTML; canonical language `zh` | `output_consistency`, `format_review`, `platform_preview` |
| `claim_ledger` | Markdown | `source_review` |
| `podcast_script_en` | DOCX | `source_review`, `readability`, `document_render` |
| `audio_mp3` | MP3 | `provider_provenance`, `audio_content`, `full_listening`, `media_duration` |
| `audio_transcript_en` | UTF-8 TXT | `transcript_alignment`, `source_review` |
| `storyboard_en` | UTF-8 TXT | `storyboard_timing`, `format_review` |
| `visual_assets` | ZIP | `visual_review`, `asset_rights` |
| `video_mp4` | MP4 | `video_sync`, `full_playback`, `format_review` |

Only roles selected by the package are required. The audio item also records `provider` as `google_notebooklm` or `google_gemini_tts`, backed by its provenance check. This preset does not accept a silent provider substitution. Platform preview means the actual chosen publishing editor, not a local browser rendering.

## Delivery items

Preparation generates each required item with `status: "pending"`. An item records:

| Field | Meaning |
| --- | --- |
| `role` | Exact deliverable ID from the preset |
| `path` | File path relative to the run directory |
| `status` | `pending`, `blocked` or `complete` |
| `reason` | Concrete blocker explanation when status is `blocked` |
| `sha256` | Actual lowercase SHA-256 of the delivered bytes |
| `author_id` | Canonical article's exact author identity for linked article outputs; actual author or producer for other roles |
| `canonical_id` | Core-manifest article ID where the role requires a canonical association |
| `checks` | Checks that were actually performed |

A blocked item includes its concrete reason. Mark an item complete only after its file and required checks exist. Its filename extension must match the selected format. Nonempty files and plausible extensions alone do not establish completion. File-format inspection does not certify document layout, audio intelligibility or video quality.

All referenced run files must stay within the run directory. Traversal, symlink escape, duplicate IDs/roles/paths, invalid hashes and malformed statuses are rejected. These checks protect a run's integrity; they are not a signature proving that its declarations are true.

## Check attestations

Each required check uses a kind defined by the preset and records:

```json
{
  "kind": "output_consistency",
  "status": "not_run",
  "reviewer_id": null,
  "reviewer_type": null,
  "reviewed_at": null,
  "artifact_sha256": null,
  "evidence": "",
  "related_hashes": {}
}
```

This example is intentionally incomplete. After the work occurs, replace the fields with the actual observation, reviewer identity and type (`agent`, `human` or `tool`), timezone-bearing timestamp and file digest. Use `pass`, `fail` or `not_run`; do not copy another check's result.

A passing attestation must identify the current item hash and the evidence for the check. Every required check must name a reviewer other than the item's author or producer, including format and measurement checks. Keep source fidelity, prose and delivery assignments independent across the entire run, including linked or later-produced formats. Keep one final article reviewer free of specialist or package-check assignments. The same delivery reviewer may inspect several technical properties. A tool identity is appropriate for a measurement the tool actually performed; it cannot stand in for source reading or listening. The program validates this record and association, not the reviewer's lived actions.

Additional check records are also validated. Do not leave stale hashes, invalid statuses or failed checks in the active record after an issue has been repaired; retain superseded records in the audit history.

For `output_consistency`, bind `related_hashes.canonical` to the current audited canonical article. `transcript_alignment` binds `related_hashes.audio_mp3` to the final audio. `storyboard_timing` and `video_sync` also identify the corresponding final audio. An audio edit therefore invalidates an old alignment check even if the transcript file has not changed.

Record measured pages or duration in the corresponding check's `measured_value`. Page measurements must be positive integers; duration must be positive. The preset defines the metric and target. Advisory misses warn; required misses prevent readiness. Chinese body counts, and an English `body_words` target when selected, come from the audited canonical text using the core's conventions. Do not widen the core manifest's count bounds to bypass a required preset target.

## Approval when applicable

The initial record sets approval to not requested and not required. This does not grant publication permission. Apply a real approval requirement only when the task or organization actually has one.

When approval is required, record its actual status, reviewer and evidence. Any decision recorded as `approved`, including optional approval, must name the reviewer and evidence and bind the current package hashes in `approval.package_hashes`, keyed by role. Subsequent content changes need the appropriate renewed approval. Do not convert an agent review into a human signature.

## Read the report

| Overall status | Meaning |
| --- | --- |
| `incomplete` | Required work or a check has not been completed |
| `blocked` | A stated missing dependency, access or other blocker prevents completion |
| `changes_required` | A failed check, invalid record or inconsistent artifact needs repair |
| `approval_pending` | An applicable approval is still missing or stale |
| `ready_for_handoff` | Required files and recorded checks satisfy the selected contract |

Read the per-item findings and the freshly generated core result. A single overall label cannot explain every issue in a partially completed package. The report explicitly includes `semantic_verification_performed: false`.

Exit code `0` means ready for handoff, `1` means the package is not ready, and `2` indicates incorrect command-line usage. Review warnings even after an exit-code-zero result.

No usage telemetry, external upload, message or publication action is performed by acceptance. A completed article package does not imply a requested podcast or video package is also complete.
