# Validation record for version 0.2.0

Date: 2026-11-17. Runtime tested on Python 3.12.14 in Linux. Python 3.9+ is the intended baseline; other hosts and AI products have not been certified by this record.

Release check: all 37 integration tests passed against the public package and the verified core files. The installed skill also passed its package validation.

## What was exercised

- A real online preparation retrieved the nine locked Evidence to Article v0.2.0 files and verified every SHA-256. Offline preparation used those same repository-relative files and the same integrity checks.
- CLI integration tests use the actual locked core checker. They cover prepared-but-empty runs, valid synthetic records, missing outputs and checks, malformed statuses, stale content/review hashes, self-review, missing claim inventories, incorrect language/canonical associations, required and claimed approvals, strict/advisory lengths, PDF signatures, dependency tampering and unsafe paths.
- Media contract tests use a short locally generated silent MP3 fixture. Provider and reviewer records are explicitly synthetic software-test data. They check provider selection, missing listening records and stale audio/transcript associations; they do not demonstrate Google generation or perceptual quality.
- A fresh agent followed the installed instructions to prepare an eleven-deliverable video run offline. Acceptance correctly returned incomplete for the missing sources, articles and media. No completed research, content, listening or publication was claimed.
- Independent code and documentation reviews identified and repaired inconsistencies in additional measurement attestations, supported formats, page measurements, optional approval claims, manifest-relative paths and cached Python execution guidance.

This validates setup and acceptance behavior within the stated scope. It does not establish that a complete real-world article/podcast/video package has been produced across multiple AI services, or that the workflow reduces editing time. Source reading, actual prose review, document previews and media review remain work performed by the host tools and identified reviewers.

## Reproduce the software tests

Prepare a disposable directory to obtain the verified dependency, using the commands in [Start here](START-HERE.md). Then run from the repository root:

```bash
EVIDENCE_ENGINE_SOURCE=/absolute/path/to/disposable-run/.engine \
  python3 -B -m unittest discover -s tests -v
```

The suite defaults to the skill in this repository. Set `PLAYBOOK_SKILL_DIR` to test another installed copy. Without `EVIDENCE_ENGINE_SOURCE`, the suite explicitly skips; a skipped suite is not a passing execution of these integration tests. The source must match the bundled lock. No external media account or real article is needed.

The test fixtures' approvals and source claims exist only to exercise the software contract. Never reuse them as production review records.
