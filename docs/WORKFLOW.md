# From a topic or research packet to a publication package

This playbook coordinates an agent's work. It does not deploy a scheduler, create service accounts, or guarantee unattended production. The reusable writing and evidence rules live in [Evidence to Article v0.2.0](https://github.com/CopernicusP/evidence-to-article/tree/ba0f2d04d3b64a67e9118273444dc19bbd8f0ccc).

## 1. Establish one run

Copy the [episode brief](../templates/episode-brief.md) into a private working location outside this public repository. Read the current request, supplied material and selected profile. The [example profile](../profiles/example.json) is an editable starting point, not an organization's policy. Record the actual profile version and core commit used.

Choose the input route:

| Input | Work to perform | First useful output |
| --- | --- | --- |
| Topic only | Define a reader question, research primary sources, reconcile findings and record gaps | Research packet with source locators and a claim ledger |
| Existing research | Read the packet, identify its cutoff and verification history, check material gaps and current status where relevant | Adaptation-ready claim ledger |
| Draft plus feedback | Read the latest draft and accessible comments; distinguish factual corrections from voice preferences | Revision plan tied to passages, followed by a repaired draft |

For topic-only work, use the [research brief](../templates/research-brief.md). A brief defines research; it is not a completed report. For existing research, preserve useful work and investigate material gaps instead of silently commissioning another report. An inherited verification label does not establish that a source was read in this run.

Select only the requested channels. Agree or infer reasonable length targets and record the assumption. A page target requires a chosen page layout and inspection of the rendered file; a word or character count cannot substitute for it. Record whether an audio duration target includes its introduction and closing.

## 2. Build the evidence packet

Use the [claim ledger](../templates/claim-ledger.md) to connect material statements to specific source locations. Prioritize original records for the facts driving the argument. Record publication dates separately from event dates and data cutoffs. Resolve contradictions by checking, narrowing or omitting the affected assertion, preserving uncertainty that changes the conclusion.

The packet should give a writer enough information to explain the subject without inventing connective facts: the central question, relevant chronology, actors and roles, supported findings, calculations where needed, counterevidence and unresolved gaps. A bibliography alone is not that packet. Keep full evidence and access records in the authorized working location.

## 3. Compose the requested channels

Invoke the pinned [core workflow](https://github.com/CopernicusP/evidence-to-article/blob/ba0f2d04d3b64a67e9118273444dc19bbd8f0ccc/skills/evidence-to-article/SKILL.md) with the brief, claim ledger and current sources. Use the [article request](../templates/article-request.md) as a compact handoff.

Chinese and English share factual commitments but need not share section order, metaphors or paragraph boundaries. Compose each for its audience using the core's [channel guidance](https://github.com/CopernicusP/evidence-to-article/blob/ba0f2d04d3b64a67e9118273444dc19bbd8f0ccc/skills/evidence-to-article/references/channels.md). The Chinese article should stand on its own as a readable explanation. The English blog should select a clear argument rather than summarize every section of the research packet.

When a more personal voice is selected, apply the core's [grounded authorial voice](https://github.com/CopernicusP/evidence-to-article/blob/ba0f2d04d3b64a67e9118273444dc19bbd8f0ccc/skills/evidence-to-article/references/authorial-voice.md). Evidence may support a visible editorial judgment; it cannot supply a fictional memory, interview or emotion. Do not force first person into every paragraph or transfer a blog preference to a research report automatically.

A podcast script is a listening adaptation with its own sequence and pronunciation notes. Actual generated audio needs a separate content check. Follow [media production](MEDIA.md) only when audio or video is requested and the required services and inputs are available.

## 4. Review, repair and export

Use the three independent review responsibilities in [quality and handoff](QUALITY.md). Reviewers receive the actual current artifacts and evidence, not an expected verdict. The coordinating agent resolves specific findings and produces the revision. A vague instruction to add “human polish” does not finish the editorial work.

After substantive repair, review the affected content again and bind decisions to the current artifact hashes. Preserve revisions as `V1`, `V2` or `Draft`; record readiness separately from filenames.

Lock one canonical text per language and derive requested text and HTML exports from it. The core's TXT helper preserves Markdown syntax; select and verify another renderer when a plain-text house layout is required. Inspect actual DOCX/PDF pages when those formats are requested. Read the core's [output contract](https://github.com/CopernicusP/evidence-to-article/blob/ba0f2d04d3b64a67e9118273444dc19bbd8f0ccc/skills/evidence-to-article/references/manifest-contract.md) before using its helpers or checker. Its v0.2.0 checker expects TXT and HTML companions for each canonical article; keep those internal if they are not requested delivery formats. Machine checks supplement source reading and editorial review.

## 5. Hand over the package

Deliver only the requested files, with their version, source cutoff, completed checks and concrete remaining gaps. Keep research, source records and review history available in the authorized archive. Publication, messaging and changes to sharing follow the user's applicable authorization; drafting permission alone does not grant those actions.

| Channel | Reader-facing deliverables | Working records |
| --- | --- | --- |
| Research | Report if requested | Sources, calculations, gaps and claim ledger |
| English blog | Requested document or web/text formats | Canonical text and review records |
| Chinese reading article | Requested TXT, HTML or document formats | Canonical text and format checks |
| Podcast | Finished audio if generated and checked | Recording script, actual audio transcript and provenance |
| Video | Finished video if produced and checked | Timecoded storyboard, permitted assets and timeline records |

An unavailable media service should result in a precise status and the completed text work, not a mislabeled audio deliverable. Record organization approval and publication separately from agent review whenever those stages apply.
