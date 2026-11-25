# Runtime validation

## Version 0.3.0

All 43 integration tests passed on Linux with Python 3.12.14 and the [locked Evidence to Article release](../skills/editorial-playbook/references/engine-lock.json). The suite runs the actual core checker against synthetic records. It exercises package setup and acceptance, required files and checks, output consistency, media bindings, stale hashes and the schema-2 review contract.

A separate end-to-end exercise prepared topic, research and draft inputs. It accepted a complete synthetic package and rejected missing specialist or whole-article reviews, conflicting reviewer assignments across languages or deliverables, stale review evidence, legacy-schema substitution and changed dependency files. Repairing an article required current specialist records and a renewed complete read. The nine locked dependency files were also checked against the exact public revision.

The software fixtures do not represent human reader tests or publication approval. The silent MP3 fixture exercises media records only. Actual source reading, prose review, listening and rendering still require the identified people, agents and tools.

## Reproduce the software tests

Prepare a disposable directory to obtain the verified dependency, using the commands in [Start here](START-HERE.md). Then run from the repository root:

```bash
EVIDENCE_ENGINE_SOURCE=/absolute/path/to/disposable-run/.engine \
  python3 -B -m unittest discover -s tests -v
```

The suite defaults to the skill in this repository. Set `PLAYBOOK_SKILL_DIR` to test another installed copy. Without `EVIDENCE_ENGINE_SOURCE`, the suite explicitly skips; a skipped suite is not a passing execution of these integration tests. The source must match the bundled lock. No external media account or real article is needed.

The test fixtures' approvals and source claims exist only to exercise the software contract. Never reuse them as production review records.
