# Start a production run

Use Editorial Playbook with a host agent that can read the workflow and the selected evidence. The bundled `bilingual-finance` preset supplies delivery requirements. Evidence to Article supplies the writing core. A new run keeps the selected requirements and actual work separate from other users' conversations.

## Give the agent the task

Use the [copyable request in the README](../README.md#start-with-one-request). Identify the topic or attached research, audience, factual cutoff, output package and authorized working location. Select only the package needed for this run.

| Package | Scope |
| --- | --- |
| `articles` | Research, English blog, Chinese TXT/HTML and claim ledger |
| `podcast` | Articles plus recording script, MP3 and final-audio transcript |
| `video` | Podcast package plus storyboard, visual assets and MP4 |

For the bundled media preset, select Google NotebookLM or Google Gemini TTS and supply permitted media assets. Its podcast outputs are English. A different provider or language requires a matching custom preset. The workflow does not carry credentials or authorize uploads, sending or publication. Routine editorial choices can proceed within the existing task without asking the user to choose every heading or rewrite each paragraph.

## Check the host's capabilities

| Capability | Work it enables | If unavailable |
| --- | --- | --- |
| Reading supplied files and original sources | Research and material-claim verification | Identify evidence gaps; do not claim unavailable sources were read |
| Python 3.9+, file access and access to the pinned core or a verified cache | Setup, dependency verification and executable acceptance | Follow available instructions with an explicitly limited status; no script-pass claim |
| Separate reviewers or agents | One independent specialist per applicable criterion and a fresh whole-article reviewer | Record limited independence; self-review cannot satisfy independent approval |
| Document rendering | Actual page counts and layout review | Keep render checks incomplete |
| Authorized speech generation, download, transcription and full listening | Finished podcast package | Deliver completed text work and report media blockers |
| Video editing, permitted assets and playback inspection | Finished video package | Keep the video package incomplete or blocked |
| Access to the destination editor | Chinese HTML platform preview required by the bundled preset | Keep that check incomplete and record local preview separately |

The setup command verifies local dependency bytes. External capabilities are declarations with supporting observations; it does not log in to services or prove those services are usable.

The accepted capability keys are `source_access`, `independent_review`, `document_rendering`, `platform_preview`, `audio_generation`, `audio_review`, `video_editing` and `video_review`. Preflight reports external stages as `declared_available`, `unknown` or `blocked`; a declaration is not an automated service-access test.

## Prepare the run

An agent with Python can run these commands from the repository root. Change the example topic, cutoff and absolute run path. Use a new directory outside the public checkout.

```bash
python3 skills/editorial-playbook/scripts/prepare_run.py \
  --run-dir /path/to/private-run \
  --topic "The reader question for this issue" \
  --input-mode topic \
  --cutoff 2026-11-17 \
  --package articles
```

Use `--input-mode research` for an existing research packet, or `draft` for revision. These values select the route; they do not import or verify an attachment. Place the actual source material in the authorized run location and identify it in the brief.

The command retrieves the files named in the bundled dependency lock and verifies their hashes. It can instead use a repository-layout source cache:

```bash
python3 skills/editorial-playbook/scripts/prepare_run.py \
  --run-dir /path/to/another-private-run \
  --topic "The reader question for this issue" \
  --input-mode research \
  --cutoff 2026-11-17 \
  --package podcast \
  --engine-source /path/to/evidence-to-article \
  --offline
```

The source folder must contain the exact locked files at their repository-relative paths. A different core version does not satisfy the lock. `--offline` requires `--engine-source`. Setup refuses to overwrite a nonempty run directory.

Add `--capabilities /path/to/capabilities.json` to provide current observations. An entry has this shape:

```json
{
  "audio_generation": {
    "status": "unavailable",
    "evidence": "No authorized speech-generation service is connected for this run."
  }
}
```

Use `available`, `unavailable` or `unknown`; absent capabilities remain unknown. Record actual observations, not hoped-for access. Missing media capability does not prevent preparation of the article work.

## Read the prepared files

| File | Purpose |
| --- | --- |
| `RUN.md` | Run-specific instructions and the actual local core entry path |
| `run.json` | Selected input route, package and bound file locations |
| `profile.json` | Snapshot of the chosen delivery preset |
| `preflight.json` | Dependency result and available, missing or unknown capabilities |
| `capabilities.json` | Capability declarations used for preparation |
| `core-manifest.json` | Sources, canonical articles, claims and real core-review records to fill |
| `delivery.json` | Required outputs and their actual production/check status |
| `.engine/` | Verified core files used by this run |

Preparation produces empty working records, not approved articles. Read `RUN.md`, follow [the editorial workflow](WORKFLOW.md), produce the requested files and record reviews only after they occur.

Keep `.engine/` unchanged. If you call a cached core Python script directly, use `python3 -B` so the run does not gain unlisted bytecode-cache files. The delivery checker rejects changed or extra dependency files.

## Customize before starting

Use a private copy of [the runtime preset](../skills/editorial-playbook/references/presets/bilingual-finance.json), then pass `--preset /path/to/custom-preset.json`. Adjust the roles selected by the existing `articles`, `podcast` and `video` packages, targets and requirements to the actual brief. The older `profiles/example.json` uses a different instructional shape and cannot be passed as a runtime preset unchanged.

Preset targets marked `advisory` produce warnings outside the suggested range. Use `required` when a range is a true acceptance requirement. Do not relax a real requirement or invent a measurement merely to obtain a pass. If scope changes after preparation, make a new run with the revised preset rather than silently rewriting a bound requirement.

## Check the finished package

After the actual writing, exports and reviews:

```bash
python3 skills/editorial-playbook/scripts/check_delivery.py \
  --run-dir /path/to/private-run \
  --report /path/to/private-run/acceptance-V1.json
```

This verifies the locked dependency again and invokes its core checker freshly. It also checks the selected package's required files and review records. Review every error and warning; repair the affected work and rerun acceptance with a new report filename such as `acceptance-V2.json`. Existing report files are not overwritten. Omit `--report` to print the result without saving it. A newly prepared run should be incomplete.

See [the delivery contract](DELIVERY-CONTRACT.md) for the records. `ready_for_handoff` means the files and recorded checks satisfy the contract. It does not mean the software independently read sources, heard the audio, granted publication permission or proved that an attestation is truthful.
