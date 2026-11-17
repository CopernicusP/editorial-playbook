# Editorial Playbook

从选题或已有研究，到可读的中文文章、英文 Blog，以及按需制作的播客和视频。

An open editorial workflow powered by **[Evidence to Article](https://github.com/CopernicusP/evidence-to-article)**. This playbook organizes research, channel requirements, production and handoff. Evidence to Article provides the reusable writing and review core.

Version **0.1.0** · [Start the workflow](skills/editorial-playbook/SKILL.md) · [Example profile](profiles/example.json) · [MIT license](LICENSE)

## Two ways to start

| Input | What the agent does |
| --- | --- |
| A topic and intended reader | Defines the research question, opens sources, builds an evidence packet, then writes and reviews requested outputs |
| Existing research or a source packet | Checks sources, dates and material gaps, then adapts the evidence into requested channels |

You do not have to supply a finished research report. Topic-only work needs a research-capable agent with access to the relevant sources. Existing drafts and editorial comments can also be supplied for revision.

This is an agent-executed playbook. It does not run a background service, supply accounts or API keys, or guarantee one-click media generation. Available tools determine which steps the agent can complete.

## Use it

Give an agent the [workflow skill](skills/editorial-playbook/SKILL.md) URL and ask it to read the linked documents, or install that folder through your agent's supported skill mechanism. It also needs access to the [pinned writing core](https://github.com/CopernicusP/evidence-to-article/tree/ba0f2d04d3b64a67e9118273444dc19bbd8f0ccc). A standalone skill installation reads this repository's documents online; use a full checkout if you need a local snapshot.

Copy one of these requests and fill in the brackets:

```text
Use editorial-playbook.
Topic: [the question to investigate]
Audience and purpose: [who needs to understand what]
Evidence cutoff: [date]
Outputs: Chinese article TXT + HTML and English blog DOCX.
Length and voice: [requirements, or use labeled example defaults]
Research the topic, verify the evidence, write each language independently,
and obtain separate readability, source accuracy and delivery reviews.
Save drafts and review records to [authorized destination].
```

```text
使用 editorial-playbook，把附件研究改编成中文公众号阅读稿和英文 Blog。
读者：[受众]；主要想讲清楚：[问题]；资料截至：[日期]。
篇幅与格式：[要求]。中文希望有依据、有个人判断，读起来像自然的中文文章。
先核验已有研究，补查实质缺口，再写作、独立复核并修订。
本次只要文章；交到：[位置]。
```

For a podcast, add language, duration, chosen provider and whether intro/outro count toward the target. Request video separately with its aspect ratio. Provider access, authorized source material and actual media checks are needed before a finished MP3 or MP4 can be reported.

## What can be delivered

| Channel | Deliverables when requested | Completion evidence |
| --- | --- | --- |
| Research | Report, source list and claim ledger | Sources actually accessed; unresolved claims identified |
| English blog | Article and requested DOCX/TXT/HTML exports | Independent reviews, actual count and document preview |
| Chinese article | Native Chinese article, TXT and matching HTML | Shared evidence, readable structure, matching visible content |
| Podcast | Recording script, MP3 and transcript of that track | Provider record, final audio check, measured duration and transcript alignment |
| Video | Timecoded storyboard, visual assets and MP4 | Final timeline, readable visuals, audio/video inspection |

Outputs are selected per run. A script is not a finished audio file, and a local preview is not a publication-platform preview. The delivery record distinguishes completed work, blocked steps and any required publication approval.

## Where each part belongs

| Layer | Responsibility |
| --- | --- |
| [Evidence to Article](https://github.com/CopernicusP/evidence-to-article) | Evidence-grounded composition, authorial voice, language adaptation, independent review and export/audit utilities |
| Editorial Playbook | Topic/research routing, editable channel profiles, media production and delivery records |
| Your organization profile | Audience, terminology, house style, approved samples and actual approval requirements |
| Your private run folder | Sources, drafts, media, comments, review records and deliverables |

The core is pinned to **v0.2.0**, commit `ba0f2d04d3b64a67e9118273444dc19bbd8f0ccc`. Its helpers do not automatically load or enforce this profile. An agent reads and applies it. Keep reusable writing improvements in the core rather than copying a second engine here.

## Customize

Start with [profiles/example.json](profiles/example.json). Lengths are editable suggestions, not universal rules or a claim about any organization's requirements. A real brief takes precedence. The example selects grounded personal voice for Chinese explanation: show a supported judgment without inventing an interview, visit or personal experience.

Follow [the workflow](docs/WORKFLOW.md), [review and handoff guide](docs/QUALITY.md) and [media guide](docs/MEDIA.md). Store reusable feedback as concrete examples and revision reasons in a private profile; do not rely on a shared chat remembering everyone's preferences.

## Contribute

Open an issue with a non-confidential example, the intended reader, output and specific passage or step that failed. Synthetic examples are welcome. Do not submit private source documents, account configuration, client drafts or internal feedback.

This initial release does not establish a measured reduction in editing time. Evaluate multiple runs: track factual corrections, structural rewrites, reader feedback and editing effort.

If the workflow is useful, consider starring the main **[Evidence to Article](https://github.com/CopernicusP/evidence-to-article)** project. Improvements to its writing core benefit all adapters.
