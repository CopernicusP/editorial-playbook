#!/usr/bin/env python3
"""Prepare a new private run and verified dependency; do not generate content."""

import argparse
from datetime import date, datetime, timezone
import json
import math
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid

from engine import CORE_PREFIX, SKILL_ROOT, digest, fetch_or_copy_engine, load_lock, relative_parts


DEFAULT_PRESET = SKILL_ROOT / "references" / "presets" / "bilingual-finance.json"
CAPABILITIES = (
    "source_access", "independent_review", "document_rendering",
    "audio_generation", "audio_review", "video_editing", "video_review", "platform_preview",
)
FORMATS = {"txt", "html", "docx", "pdf", "mp3", "mp4", "zip", "md", "json"}


def read_object(path, label):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError(label + " must be a regular JSON file smaller than 2 MiB")
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(label + " must be a JSON object")
    return obj


def validate_preset(profile):
    if type(profile.get("schema_version")) is not int or profile["schema_version"] != 1:
        raise ValueError("Unsupported preset schema")
    for key in ("id", "version", "description"):
        if not isinstance(profile.get(key), str) or not profile[key].strip():
            raise ValueError("Preset needs a nonempty " + key)
    packages, roles = profile.get("packages"), profile.get("deliverables")
    if not isinstance(packages, dict) or not packages or not isinstance(roles, dict) or not roles:
        raise ValueError("Preset needs nonempty packages and deliverables objects")
    paths = set()
    for role, item in roles.items():
        if not isinstance(role, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", role) or not isinstance(item, dict):
            raise ValueError("Invalid preset deliverable role")
        path = item.get("path")
        relative_parts(path)
        if path in paths:
            raise ValueError("Duplicate preset deliverable path")
        paths.add(path)
        if item.get("format") not in FORMATS:
            raise ValueError("Unknown format for " + role)
        if not path.lower().endswith("." + item["format"]):
            raise ValueError("Deliverable extension differs from its format: " + role)
        checks = item.get("checks")
        if (not isinstance(checks, list) or not checks or
                any(not isinstance(x, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", x) for x in checks) or
                len(checks) != len(set(checks))):
            raise ValueError("Deliverable needs unique check names: " + role)
        if "canonical_language" in item and item["canonical_language"] not in ("zh", "en"):
            raise ValueError("Canonical language must be zh or en")
        if "allowed_providers" in item:
            providers = item["allowed_providers"]
            if (not isinstance(providers, list) or not providers or
                    any(not isinstance(value, str) or not value.strip() for value in providers) or
                    len(providers) != len(set(providers))):
                raise ValueError("Allowed providers must be unique nonempty strings: " + role)
        if "target" in item:
            target = item["target"]
            if (not isinstance(target, dict) or target.get("enforcement") not in ("advisory", "required") or
                    target.get("metric") not in ("rendered_pages", "duration_seconds", "body_Han_characters", "body_words")):
                raise ValueError("Invalid length/duration target for " + role)
            minimum, maximum = target.get("min"), target.get("max")
            if (type(minimum) not in (int, float) or type(maximum) not in (int, float) or
                    not math.isfinite(minimum) or not math.isfinite(maximum) or minimum < 0 or maximum < minimum):
                raise ValueError("Invalid target bounds for " + role)
            metric = target["metric"]
            if metric == "rendered_pages" and not set(checks) & {"document_render", "rendered_pages"}:
                raise ValueError("Rendered-page target requires a document-render measurement check: " + role)
            if metric == "duration_seconds" and not set(checks) & {"media_duration", "duration_seconds"}:
                raise ValueError("Duration target requires a media-duration measurement check: " + role)
            if metric == "body_Han_characters" and item.get("canonical_language") != "zh":
                raise ValueError("Han-character target requires a Chinese canonical article: " + role)
            if metric == "body_words" and item.get("canonical_language") != "en":
                raise ValueError("Word-count target requires an English canonical article: " + role)
    for package, members in packages.items():
        if (not isinstance(package, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", package) or
                not isinstance(members, list) or not members or
                any(not isinstance(member, str) or member not in roles for member in members) or
                len(members) != len(set(members))):
            raise ValueError("Invalid package or package roles")
    if "capabilities" in profile:
        requirements = profile["capabilities"]
        if not isinstance(requirements, dict):
            raise ValueError("Preset capabilities must be an object")
        for group, names in requirements.items():
            if (group not in {"common", *packages} or not isinstance(names, list) or
                    any(name not in CAPABILITIES for name in names) or len(names) != len(set(names))):
                raise ValueError("Invalid preset capability requirements")
    return profile


def active_page_targets(plan):
    """Read current render targets. The pinned core validates the full plan at acceptance."""
    rounds = plan.get("rounds")
    if not isinstance(rounds, list) or not rounds:
        raise ValueError("Revision plan requires source-located requirements organized in rounds")
    active = {}
    for stage in rounds:
        if not isinstance(stage, dict) or not isinstance(stage.get("requirements"), list):
            raise ValueError("Each revision round requires a requirements list")
        for requirement in stage["requirements"]:
            if not isinstance(requirement, dict) or not isinstance(requirement.get("id"), str):
                raise ValueError("Each revision requirement needs an ID")
            superseded = requirement.get("supersedes", [])
            if not isinstance(superseded, list) or any(not isinstance(key, str) for key in superseded):
                raise ValueError("Supersedes must list earlier requirement IDs")
            for key in superseded:
                active.pop(key, None)
            if "page_range" in requirement:
                target = requirement["page_range"]
                if (not isinstance(target, dict) or not isinstance(target.get("delivery_role"), str)
                        or any(type(target.get(key)) not in (int, float) or not math.isfinite(target[key])
                               for key in ("min", "max")) or not 0 < target["min"] <= target["max"]):
                    raise ValueError("A body-page range requires a delivery_role and finite, ordered bounds")
                active[requirement["id"]] = requirement
    return list(active.values())


def load_capabilities(path=None):
    supplied = read_object(path, "Capabilities") if path is not None else {}
    if set(supplied) - set(CAPABILITIES):
        raise ValueError("Unknown capability names: " + ", ".join(sorted(set(supplied) - set(CAPABILITIES))))
    result = {}
    for name in CAPABILITIES:
        item = supplied.get(name, {"status": "unknown", "evidence": "No capability observation supplied"})
        if (not isinstance(item, dict) or item.get("status") not in ("available", "unavailable", "unknown") or
                not isinstance(item.get("evidence"), str) or not item["evidence"].strip()):
            raise ValueError("Capability needs status and nonempty evidence: " + name)
        result[name] = {"status": item["status"], "evidence": item["evidence"], "basis": "operator_declaration"}
    return result


def preflight(capabilities, profile, package, engine_result):
    roles = profile["packages"][package]
    formats = {profile["deliverables"][role]["format"] for role in roles}
    stages = {"research": ["source_access"], "editorial_review": ["independent_review"]}
    if formats & {"docx", "pdf"}:
        stages["document_export"] = ["document_rendering"]
    if "mp3" in formats:
        stages["audio"] = ["audio_generation", "audio_review"]
    if "mp4" in formats:
        stages["video"] = ["video_editing", "video_review"]
    if any("platform_preview" in profile["deliverables"][role]["checks"] for role in roles):
        stages["platform_preview"] = ["platform_preview"]
    requirements = profile.get("capabilities", {})
    extra = list(dict.fromkeys(requirements.get("common", []) + requirements.get(package, [])))
    represented = {capability for required in stages.values() for capability in required}
    if set(extra) - represented:
        stages["preset_requirements"] = [capability for capability in extra if capability not in represented]
    for name, required in list(stages.items()):
        unavailable = [x for x in required if capabilities[x]["status"] == "unavailable"]
        unknown = [x for x in required if capabilities[x]["status"] == "unknown"]
        stages[name] = {
            "status": "blocked" if unavailable else "unknown" if unknown else "declared_available",
            "required_capabilities": required, "unavailable": unavailable, "unknown": unknown,
        }
    return {
        "schema_version": 1, "setup_complete": True,
        "machine_checks": {"python": {"status": "available", "version": ".".join(map(str, sys.version_info[:3]))},
                           "writing_core": engine_result},
        "stages": stages, "capability_observations_are_declarations": True,
        "semantic_verification_performed": False,
        "note": "Setup does not establish access to sources, independent agents, rendering or media services. Continue available work; resolve stage-specific gaps before claiming completion.",
    }


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare(args):
    if sys.version_info < (3, 9):
        raise ValueError("Python 3.9 or newer is required")
    if not isinstance(args.topic, str) or not args.topic.strip():
        raise ValueError("Topic must not be empty")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.cutoff):
        raise ValueError("Cutoff must use YYYY-MM-DD")
    date.fromisoformat(args.cutoff)
    profile = validate_preset(read_object(args.preset, "Preset"))
    if args.package not in profile["packages"]:
        raise ValueError("Selected package does not exist in the preset")
    capabilities = load_capabilities(args.capabilities)
    lock = load_lock()
    target = Path(args.run_dir).expanduser()
    if target.is_symlink():
        raise ValueError("Run directory must not be a symbolic link")
    target = target.resolve()
    if target == SKILL_ROOT or SKILL_ROOT in target.parents:
        raise ValueError("Create runs outside the installed skill")
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ValueError("Run directory must be new or empty; existing data will not be overwritten")
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="." + target.name + ".prepare-", dir=str(target.parent)))
    try:
        engine_result = fetch_or_copy_engine(staging / ".engine", lock, args.engine_source, args.offline)
        write_json(staging / "profile.json", profile)
        now = datetime.now(timezone.utc).isoformat()
        run = {
            "schema_version": 1, "run_id": uuid.uuid4().hex, "created_at": now,
            "topic": args.topic.strip(), "input_mode": args.input_mode, "source_cutoff": args.cutoff,
            "package": args.package, "preset_path": "profile.json",
            "preset_sha256": digest((staging / "profile.json").read_bytes()),
            "engine_dir": ".engine", "core_manifest": "core-manifest.json",
            "delivery_manifest": "delivery.json",
            "engine": {key: lock[key] for key in ("name", "version", "repository", "commit")},
        }
        manifest = {"schema_version": 2, "integrator_id": None, "artifacts": [], "sources": [], "claims": [], "reviews": []}
        page_targets = []
        plan_file = "revision-plan.json"
        if args.revision_plan is not None:
            if args.revision_plan.is_symlink() or not args.revision_plan.is_file() or args.revision_plan.stat().st_size > 2 * 1024 * 1024:
                raise ValueError("Revision plan must be a regular JSON file smaller than 2 MiB")
            snapshot = staging / plan_file
            shutil.copyfile(args.revision_plan, snapshot)
            plan = read_object(snapshot, "Revision plan")
            page_targets = active_page_targets(plan)
            for requirement in page_targets:
                role = requirement["page_range"]["delivery_role"]
                if role not in profile["packages"][args.package] or profile["deliverables"][role]["format"] not in ("docx", "pdf"):
                    raise ValueError("Body-page target requires a selected DOCX or PDF delivery role: " + role)
            plan_binding = {"plan_path": plan_file, "plan_sha256": digest(snapshot.read_bytes())}
            run["revision_plan"] = plan_binding
            manifest["cumulative_revision"] = {**plan_binding, "checks": {}}
        write_json(staging / "run.json", run)
        items = [{"role": role, "path": profile["deliverables"][role]["path"], "status": "pending",
                  "sha256": None, "author_id": None, "canonical_id": None, "checks": []}
                 for role in profile["packages"][args.package]]
        for item in items:
            if "allowed_providers" in profile["deliverables"][item["role"]]:
                item["provider"] = None
        write_json(staging / "delivery.json", {
            "schema_version": 1,
            "items": items,
            "approval": {"required": False, "status": "not_requested", "reviewer_id": None, "evidence": None},
        })
        write_json(staging / "core-manifest.json", manifest)
        write_json(staging / "capabilities.json", capabilities)
        report = preflight(capabilities, profile, args.package, engine_result)
        write_json(staging / "preflight.json", report)
        core_skill = target / ".engine" / CORE_PREFIX / "SKILL.md"
        checks = target / ".engine" / CORE_PREFIX / "scripts" / "check_run.py"
        instructions = """# Prepared editorial run

Preparation only: no research, article, audio, video, review or publication has been completed.

- Read `run.json`, `profile.json` and `preflight.json` for this run's scope and gaps.
- For a revision, reconstruct the commission and accepted changes through the latest instructions. Compare the supplied versions by their contents and provenance. Carry forward each active requirement, including any requested comparison. Record the location and reason for a superseding decision.
- Read the verified core entry: `{core_skill}`. Follow its local relative references.
- Use the schema-2 `core-manifest.json` and the verified core's `references/manifest-contract.md`. Identify the one writer who integrates the run in `integrator_id`. Declare each article's `required_criteria` before assigning reviewers.
- Include `readability`, `source_meaning` and `delivery`. Scope `number_relevance`, `reader_implications`, `reader_teachback`, `closing_synthesis` and `comment_closure`; put a concrete reason for each inapplicable one in that article's `inapplicable_criteria` object. Add further criteria from the brief.
- When an explanation depends on unfamiliar knowledge, give the separate `reader_teachback` reviewer the article and audience description alone for their first read. Record their own explanation of who does what, why it matters, and the precise missing step. Label an agent or human reading accurately.
- Assign a different independent reviewer to each applicable criterion. Preserve comment IDs and anchors. One writer integrates findings. After the affected specialists recheck and the others renew decisions on the current version, one fresh reviewer reads the complete integrated work across all requested languages. Assign identities consistently across the run. A specialist may cover the same criterion across both languages. Further edits reopen affected checks and the final read.
- Record actual reviewers, types, versions, source evidence and limitations. Technical checks, agent readings and direct human feedback each have their own provenance.
- Write each requested deliverable, then record its current hash and actual checks in `delivery.json`.
- The core checker is `{checks}`. The wrapper's `scripts/check_delivery.py --run-dir` invokes it again before accepting the package.
- Keep the recording script distinct from the transcript of the finished audio. Mark unavailable stages blocked with a reason.
- The initial manifests intentionally cannot pass acceptance. Do not invent identities, measurements, sources or completed checks to fill them.
- No material has been sent or published. Publication permissions and any real organization approval remain separate.

The preparation program verified dependency bytes and local Python. Other capability observations are declarations, not automated capability tests. The default manifests contain no private account information; keep later evidence and deliverables in this authorized run directory.

## Run the core without modifying its cache

From this run directory, export the actual canonical articles and check their completed manifest with:

```bash
python3 -B .engine/skills/evidence-to-article/scripts/build_outputs.py --input article-zh.md --out-dir audit
python3 -B .engine/skills/evidence-to-article/scripts/build_outputs.py --input article-en.md --out-dir audit
python3 -B .engine/skills/evidence-to-article/scripts/check_run.py --manifest core-manifest.json{cumulative_flag}
```

Use `-B` for every direct core execution, including when following commands in the core's own documentation. It prevents Python from creating `__pycache__` inside the strictly verified `.engine` cache. The wrapper checker uses `-B` itself. If an earlier command created cache files, inspect them before removing only those generated cache files, or prepare a fresh run with the verified source. Never delete arbitrary dependency files or modify the lock to bypass an integrity failure. Setup does not automatically clean an existing run.
""".format(core_skill=core_skill, checks=checks, cumulative_flag=" --require-cumulative" if args.revision_plan else "")
        if args.revision_plan:
            instructions += (
                "\n## Cumulative revision\n\n"
                "Use the frozen `revision-plan.json` and the pinned manifest contract. Give the distinct "
                "`revision_continuity` reviewer the commission, agreed changes, evidence and current articles. "
                "Trace every active requirement to an exact current passage. Stage any archived plan and accepted fixes "
                "at their declared run-relative paths. Bind the specialist and holistic reads to both the plan hash "
                "and the current checks digest. Measure body-page ranges on the final delivery render, excluding references "
                "and unused space. A new user instruction changing the plan needs a new run snapshot.\n"
            )
        instructions += "\n## Requested deliverables\n\n| Role | Path | Target |\n| --- | --- | --- |\n"
        for role in profile["packages"][args.package]:
            item = profile["deliverables"][role]
            target_spec = item.get("target")
            target_text = ("{min}–{max} {metric} ({enforcement})".format(**target_spec)
                           if target_spec else "No numerical target")
            body_targets = [record["page_range"] for record in page_targets if record["page_range"]["delivery_role"] == role]
            if body_targets:
                current = " and ".join("{min}–{max} body-page equivalents".format(**bounds) for bounds in body_targets)
                target_text = current if not target_spec or target_spec["metric"] == "rendered_pages" else target_text + ", " + current
            instructions += "| {} | `{}` | {} |\n".format(role, item["path"], target_text)
        instructions += "\nUse the bound preset and any current body-page target in the frozen revision plan. Record real measurements and deviations; do not modify the brief just to obtain a pass.\n"
        (staging / "RUN.md").write_text(instructions, encoding="utf-8")
        if target.exists():
            if target.is_symlink() or not target.is_dir() or any(target.iterdir()):
                raise ValueError("Run destination changed during preparation; existing data was preserved")
            target.rmdir()
        staging.rename(target)
        return {"ok": True, "status": "prepared", "run_dir": str(target),
                "core_entry": str(core_skill), "preflight": report,
                "next": "Read RUN.md and perform the requested work; setup is not editorial completion."}
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--input-mode", required=True, choices=("topic", "research", "draft"))
    parser.add_argument("--cutoff", required=True)
    parser.add_argument("--package", default="articles", choices=("articles", "podcast", "video"))
    parser.add_argument("--revision-plan", type=Path, help="Bind the source-located cumulative revision plan to this run")
    parser.add_argument("--preset", type=Path, default=DEFAULT_PRESET)
    parser.add_argument("--capabilities", type=Path)
    parser.add_argument("--engine-source", type=Path)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    try:
        result = prepare(args)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result = {"ok": False, "status": "setup_failed", "error": str(exc), "semantic_verification_performed": False}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
