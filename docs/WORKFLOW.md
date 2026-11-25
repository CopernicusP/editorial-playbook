# From a topic or research packet to a delivery package

The playbook prepares and audits a run; the host agent performs research, writing and production. Use [Start here](START-HERE.md) to select the preset and package. The writing and evidence methods remain in [Evidence to Article v0.3.0](https://github.com/CopernicusP/evidence-to-article/tree/064f31c978860ecbb8c9c2162900e82568946c7e).

## 1. Prepare the current task

Read the request, supplied material and applicable feedback. Establish the audience, central question, source cutoff and authorized working location. Select `articles`, `podcast` or `video` and any justified preset override. Run preparation when the host can execute Python, then read the resulting `RUN.md`, preset snapshot and preflight report.

Keep sources and actual outputs in the private run folder. The prepared records begin pending; setup does not create approvals. Record unavailable evidence or tools precisely while continuing independent work that can be completed.

| Input | Work to perform |
| --- | --- |
| Topic | Define a research question, open original sources, reconcile findings and build the evidence packet |
| Existing research | Read the packet, inspect its cutoff and source support, investigate material gaps, and reuse sound work |
| Draft and feedback | Read the latest text and accessible comments, retain each comment ID and original anchor, then verify its disposition against the revised passage |

A [research brief](../templates/research-brief.md) defines the work and is not a research report. An inherited “verified” label does not establish that a source was read in this run.

## 2. Build the evidence packet

Use the [claim ledger](../templates/claim-ledger.md) to connect material claims to precise source locations. Distinguish publication dates, event dates and data cutoffs. Resolve contradictions by checking, narrowing or omitting claims; preserve uncertainty and counterevidence that change the conclusion.

The packet should include the question, relevant chronology, actors and roles, supported findings, calculations where useful and unresolved gaps. A bibliography alone is not that packet. For an existing research input, adapt or export it only as needed to meet the selected research-deliverable requirements.

## 3. Compose through the core

Read the actual local core entry shown in `RUN.md` and its relevant references. Give the writer the brief, selected preset, evidence packet and current claim ledger. The [article request](../templates/article-request.md) provides a compact handoff.

Compose Chinese and English independently from shared factual commitments. Their section order and paragraph boundaries may differ. Use the core's [channel guidance](https://github.com/CopernicusP/evidence-to-article/blob/064f31c978860ecbb8c9c2162900e82568946c7e/skills/evidence-to-article/references/channels.md) and the preset's selected voice.

For a personal explanatory voice, apply [grounded authorial judgment](https://github.com/CopernicusP/evidence-to-article/blob/064f31c978860ecbb8c9c2162900e82568946c7e/skills/evidence-to-article/references/authorial-voice.md). Show which evidence deserves attention and why without inventing a memory, interview or experience. Chinese headings should carry concrete statements and advance the argument; emphasis should help the reader locate meaning.

For podcast or video packages, follow [media production](MEDIA.md). The recording script and transcript of the finished audio serve different purposes. New assertions introduced by generated speech need evidence checks.

## 4. Review, repair and export

Use the independent responsibilities in [quality review](QUALITY.md). Reviewers receive the actual brief, current files and source locations without an expected verdict. The coordinator resolves their specific findings and writes the revision.

Keep V1/V2/Draft versions and bind each decision to the actual current hash. After one writer integrates repairs, affected specialists recheck the changed passages, and the others inspect the difference before renewing their decisions. A fresh reviewer reads the integrated article end to end. If that article changes, repeat the affected checks and the final read.

Lock a canonical Markdown article per language and prepare the core manifest. The core checker requires matching TXT and HTML companions for each article, even when those exports remain internal. Its TXT helper preserves Markdown syntax; where the reader-facing TXT needs plain text, use and verify a suitable renderer and retain the core companions separately. The delivered document and its audited canonical article must remain linked.

Inspect actual DOCX pages for page counts and layout. Check visible text and links in HTML. Report a destination-platform preview only when performed there. Record audio duration and full listening on the final file, then synchronize transcript and video records after any edit.

## 5. Accept and hand over

Complete `delivery.json` with the real file locations, hashes, authors and checks. Run `check_delivery.py` as described in [Start here](START-HERE.md). It invokes the verified core checker and evaluates the selected package's delivery requirements.

The [acceptance report](DELIVERY-CONTRACT.md) distinguishes incomplete work, blocked tasks, required changes, pending approval and readiness for handoff. Fix specific problems and rerun the check; do not rename a draft to imply completion.

Deliver the requested package with its version, evidence cutoff, completed checks and remaining limitations. Keep research and review history in the authorized archive. Publication, messaging and changes to sharing require the user's applicable authorization and remain separate from an acceptance pass.
