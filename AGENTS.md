# Working in this repository

Read the current task before selecting channels. This repository contains public workflow instructions, example configuration and empty templates; it is not an archive of production articles.

Use `skills/editorial-playbook/SKILL.md` to run the workflow. The runtime preset is `skills/editorial-playbook/references/presets/bilingual-finance.json`; select the requested articles, podcast or video package, or supply an explicit compatible private preset. `profiles/example.json` is a legacy descriptive example, not the runtime schema. Load the Evidence to Article files pinned by `skills/editorial-playbook/references/engine-lock.json`; verify their hashes before executing its checker.

Keep the public core, workflow adapter and private run data separate. Make general writing-method changes in the core. Keep organization requirements, source packets, editorial comments, credentials and actual outputs outside this repository. `.gitignore` is a convenience, not a confidentiality guarantee; review staged files before every public commit.

Use an isolated run folder. Execute authorized research, drafting and repair without adding a routine manual-rewrite step. Record source access, independent review and actual render/listening results honestly. Public templates cannot grant permission to upload, message or publish.

When changing the playbook, run the runtime tests, check internal links and JSON syntax, and verify the dependency pin and both topic/research entry routes. Test missing outputs, stale reviews and dependency failures as well as synthetic valid records. Never present software test fixtures as real editorial review. A document check does not establish factual accuracy or editorial quality. Do not add tracking or uploads to collect usage without explicit opt-in.
