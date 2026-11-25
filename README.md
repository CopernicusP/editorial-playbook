# Editorial Playbook

从主题或已有研究开始，按一套明确的交付要求完成中英文文章，以及按需制作的播客和视频。

Editorial Playbook coordinates research, production and handoff using **[Evidence to Article](https://github.com/CopernicusP/evidence-to-article)** as its writing and review core. The bundled preset contains general bilingual financial-editorial requirements, without company branding, private accounts or internal source material.

Version **0.3.0** · [Start here](docs/START-HERE.md) · [Workflow skill](skills/editorial-playbook/SKILL.md) · [Delivery preset](skills/editorial-playbook/references/presets/bilingual-finance.json) · [MIT license](LICENSE)

## Start with one request

Give your agent the [workflow skill](skills/editorial-playbook/SKILL.md) and use this prompt. It accepts a topic, an existing research packet, or a draft with comments.

```text
使用 editorial-playbook 的 bilingual-finance 预设。
输入：[主题，或附上已有研究／待修改稿件]
读者与核心问题：[谁需要弄清什么]
资料截至：[日期]
交付包：articles
工作与交付位置：[允许保存资料的位置]

请加载指定版本的 Evidence to Article，先检查所需工具和资料权限。
如果只有主题，先做研究；如果已有研究，先核验并补查实质缺口。
独立撰写中文和英文，每项适用标准交给一位不同的独立审稿人。分别核查文笔、事实和交付，
以及数字是否值得保留、对目标读者有何影响、结尾是否回答开篇和批注是否逐条落实。
由一位主笔整合，相关审稿人复核改稿后，再请一位未参与的审稿人通读全文。
若再改稿，复核受影响的项目并重新通读，最后逐项验收交付文件。
中文采用有依据的个人判断，避免机械翻译、反问式小标题和多余加粗。
请说明实际完成、未完成和受阻的部分，不把未执行的检查写成通过。
```

Choose `articles`, `podcast`, or `video`. The bundled media preset uses English audio from Google NotebookLM or Google Gemini TTS; specify which product and provide authorized assets. For video, specify the aspect ratio. Use a custom preset for other provider or language requirements. Existing research can be reused as the research deliverable once it meets the selected requirements; the workflow does not require needless regeneration.

## Select a delivery package

Packages are cumulative. The [preset](skills/editorial-playbook/references/presets/bilingual-finance.json) is the machine-readable source for exact roles, formats, checks and targets.

| Package | Requested deliverables |
| --- | --- |
| `articles` | English research document, English blog, Chinese article TXT and HTML, and claim ledger |
| `podcast` | All article deliverables, plus an English recording script, MP3 and transcript of the finished audio |
| `video` | All podcast deliverables, plus a timecoded storyboard, visual-asset archive and MP4 |

The preset suggests 15–20 research pages, 2–3 English blog body pages, 2,000–3,000 Chinese body Han characters and approximately 10 minutes of audio including bookends. These are editable targets. A page target requires an actual render; it cannot be inferred from word count. Use a custom preset when the brief calls for a different scope or strict bounds.

The bundled Chinese HTML requirement includes a preview in the chosen publishing editor. A local HTML preview alone leaves that check incomplete.

## What the executable workflow adds

- **Prepare a run:** load the selected preset, retrieve or reuse the pinned core, verify its file hashes, create the delivery checklist and report declared tool availability.
- **Perform the work:** the host agent conducts research, writes, delegates review, exports documents and uses authorized media services.
- **Check delivery:** invoke the verified Evidence to Article checker and validate the selected package's files, current hashes, required review records and related audio/text versions.

The Python commands prepare and audit the work. They do not generate articles themselves, provide a speech service, certify factual truth or publish content. Missing capabilities remain visible instead of being turned into a successful completion.

See [Start here](docs/START-HERE.md) for the commands and [the delivery contract](docs/DELIVERY-CONTRACT.md) for exact records and statuses.

## Responsibilities and capabilities

| Component | Responsibility |
| --- | --- |
| [Evidence to Article](https://github.com/CopernicusP/evidence-to-article) | Composition, grounded authorial voice, independent editorial review, canonical exports and core audit |
| Editorial Playbook | Preset selection, verified dependency loading, capability preparation and package acceptance |
| Host agent and connected tools | Research access, code execution, document rendering, independent reviewers and requested media production |
| Private run folder | Actual sources, drafts, comments, media, checks and deliverables |

A text-only AI can use the writing instructions, but cannot claim to have run scripts or generated files it cannot produce. Full packages require the capabilities listed in [Start here](docs/START-HERE.md). Support is capability-dependent; this repository does not promise identical execution in every AI product.

The core is pinned to **v0.3.0**, commit `064f31c978860ecbb8c9c2162900e82568946c7e`. The [dependency lock](skills/editorial-playbook/references/engine-lock.json) identifies the exact source files. This repository does not maintain a second copy of the writing engine.

## Customize and contribute

Copy the bundled preset into an authorized private location, adjust its delivery requirements and provide it with `--preset`. Keep private organization rules, samples, account details and production runs outside this public repository. The older [example profile](profiles/example.json) remains an instructional example; it is not the runtime preset schema.

A useful issue includes non-confidential input, the intended reader, the actual output or command result, and the precise failure. Use synthetic examples unless real material is cleared for public use. Track factual corrections, structural rewrites and actual editing effort when evaluating improvements.

See the [validation record and test instructions](docs/VALIDATION.md) for the actual exercised scope and remaining limitations.

No usage telemetry or automatic starring is included. If the workflow helps your work, consider starring the main **[Evidence to Article](https://github.com/CopernicusP/evidence-to-article)** project.
