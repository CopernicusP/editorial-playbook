#!/usr/bin/env python3
"""Check a delivery package and its recorded attestations; never certify prose."""

import argparse
from datetime import date, datetime
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import zipfile

from engine import load_lock, verify_engine


MAX_JSON = 16 * 1024 * 1024
MAX_TEXT = 32 * 1024 * 1024
DIGEST = re.compile(r"[0-9a-f]{64}\Z")
STATES = ("changes_required", "blocked", "incomplete", "approval_pending")
REQUIRED_ARTICLE_CRITERIA = {"readability", "source_meaning", "delivery"}
SCOPED_ARTICLE_CRITERIA = {"number_relevance", "reader_implications", "closing_synthesis", "comment_closure"}
SCOPE = (
    "Checks files, dependency integrity, a freshly executed Evidence to Article "
    "audit, and declared review attestations. It does not read sources, judge "
    "prose, establish that reviews really occurred, or authorize publication."
)


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def safe_path(base, value):
    """Use portable, relative paths, with no symlink component or traversal."""
    if not nonblank(value) or "\\" in value or "\0" in value:
        raise ValueError("path must be a nonempty portable relative path")
    relative = PurePosixPath(value)
    if relative.is_absolute() or any(p in ("..", ".") for p in value.split("/")):
        raise ValueError("absolute paths and dot components are not allowed")
    if any(not p for p in value.split("/")) or ":" in relative.parts[0]:
        raise ValueError("empty path components and drive paths are not allowed")
    current = base
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink paths are not allowed")
    resolved = current.resolve()
    try:
        resolved.relative_to(base.resolve())
    except ValueError:
        raise ValueError("path escapes the run directory")
    return resolved


def read_object(path):
    if not path.is_file() or path.stat().st_size > MAX_JSON:
        raise ValueError("missing or oversized JSON file: " + path.name)
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError("JSON root must be an object: " + path.name)
    return result


def valid_stamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except (ValueError, TypeError, AttributeError):
        return False


def inspect_file(path, kind):
    """Return limited format evidence. Content quality remains a real review."""
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("file is missing or empty")
    if path.suffix.lower() != "." + kind:
        raise ValueError("filename extension must match the requested " + kind + " format")
    with path.open("rb") as source:
        head = source.read(65536)
    if kind == "pdf":
        if not head.startswith(b"%PDF-"):
            raise ValueError("PDF signature was not found")
        return {"inspection": "signature_only", "rendering_verified": False}
    if kind in ("txt", "html", "md", "json"):
        if path.stat().st_size > MAX_TEXT:
            raise ValueError("text file exceeds the supported size")
        text = path.read_text(encoding="utf-8")
        if text.startswith("\ufeff") or not text.strip() or "\0" in text:
            raise ValueError("text must be nonempty UTF-8 without BOM or NUL")
        if kind == "html" and not re.search(r"<(?:html|body|article|section|p)\b", text, re.I):
            raise ValueError("HTML markup was not found")
        if kind == "json":
            json.loads(text)
        return {"inspection": "utf8_and_basic_structure"}
    if kind in ("docx", "zip"):
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            names = [entry.filename for entry in entries]
            if not entries or len(entries) > 10000 or len(names) != len(set(names)):
                raise ValueError("archive is empty, too large, or has duplicate members")
            for entry in entries:
                item = PurePosixPath(entry.filename)
                if (not item.parts or item.is_absolute() or ".." in item.parts or "\\" in entry.filename
                        or ":" in item.parts[0] or stat.S_ISLNK(entry.external_attr >> 16)):
                    raise ValueError("unsafe archive member")
            if kind == "docx" and not {"[Content_Types].xml", "_rels/.rels", "word/document.xml"}.issubset(names):
                raise ValueError("DOCX is missing required OOXML parts")
        return {"inspection": "archive_structure_only"}
    if kind in ("mp3", "mp4"):
        if kind == "mp3":
            offset = 0
            if head.startswith(b"ID3"):
                if len(head) < 10 or any(byte & 128 for byte in head[6:10]):
                    raise ValueError("invalid ID3 header")
                offset = 10 + sum(byte << shift for byte, shift in zip(head[6:10], (21, 14, 7, 0)))
                if head[5] & 16:
                    offset += 10
                if offset > 16 * 1024 * 1024:
                    raise ValueError("ID3 metadata is too large")
                with path.open("rb") as source:
                    source.seek(offset)
                    head = source.read(4096)
            if not any(head[i] == 255 and head[i + 1] & 0xE0 == 0xE0
                       and head[i + 1] & 0x18 != 0x08 and head[i + 1] & 0x06 != 0
                       and head[i + 2] & 0xF0 not in (0, 0xF0) and head[i + 2] & 0x0C != 0x0C
                       for i in range(max(0, len(head) - 3))):
                raise ValueError("MPEG audio frame header was not found")
        elif len(head) < 12 or head[4:8] != b"ftyp":
            raise ValueError("MP4 ftyp header was not found")
        probe = shutil.which("ffprobe")
        if probe:
            proc = subprocess.run(
                [probe, "-v", "error", "-protocol_whitelist", "file,pipe", "-show_entries", "format=duration:stream=codec_type,codec_name",
                 "-of", "json", str(path)], capture_output=True, text=True, timeout=25,
            )
            if proc.returncode:
                raise ValueError("ffprobe could not read the media")
            info = json.loads(proc.stdout)
            streams = info.get("streams", [])
            needed = "audio" if kind == "mp3" else "video"
            if not any(s.get("codec_type") == needed for s in streams):
                raise ValueError("required media stream was not found")
            if kind == "mp3" and not any(s.get("codec_name") == "mp3" for s in streams):
                raise ValueError("audio encoding is not MP3")
            duration = float(info.get("format", {}).get("duration", "nan"))
            if not math.isfinite(duration) or duration <= 0:
                raise ValueError("media duration is invalid")
            return {"inspection": "ffprobe_structure", "duration_seconds": duration,
                    "perceived_quality_verified": False}
        return {"inspection": "signature_only", "perceived_quality_verified": False}
    raise ValueError("unsupported format: " + str(kind))


def validate_article_criteria(artifact):
    identifier = artifact["id"]
    criteria = artifact.get("required_criteria")
    exclusions = artifact.get("inapplicable_criteria", {})
    if not isinstance(criteria, list) or any(not nonblank(name) for name in criteria):
        raise ValueError(identifier + " requires a list of applicable article criteria")
    if not isinstance(exclusions, dict) or any(not nonblank(reason) for reason in exclusions.values()):
        raise ValueError(identifier + " requires a concrete reason for each inapplicable criterion")
    active = set(criteria)
    if active.intersection(exclusions):
        raise ValueError(identifier + " declares a criterion both applicable and inapplicable")
    missing = (REQUIRED_ARTICLE_CRITERIA - active) | (SCOPED_ARTICLE_CRITERIA - active - exclusions.keys())
    if missing:
        raise ValueError(identifier + " has unaccounted article criteria: " + ", ".join(sorted(missing)))


def audit(run_dir):
    issues, items_report = [], []
    result = {"schema_version": 1, "ok": False, "status": "incomplete",
              "semantic_verification_performed": False, "scope": SCOPE,
              "review_evidence_type": "recorded_attestations_not_independently_proven",
              "items": items_report, "issues": issues, "core_audit": None}

    def issue(code, message, state="changes_required", role=None, warning=False):
        record = {"code": code, "message": message, "severity": "warning" if warning else "error"}
        if not warning:
            record["state"] = state
        if role:
            record["role"] = role
        issues.append(record)

    def finish():
        states = {item.get("state") for item in issues if item["severity"] == "error"}
        result["status"] = next((state for state in STATES if state in states), "ready_for_handoff")
        result["ok"] = result["status"] == "ready_for_handoff"
        result["error_count"] = sum(x["severity"] == "error" for x in issues)
        result["warning_count"] = sum(x["severity"] == "warning" for x in issues)
        for row in items_report:
            row_issues = [x for x in issues if x.get("role") == row["role"]]
            row["issues"] = row_issues
            row_states = {x.get("state") for x in row_issues if x["severity"] == "error"}
            row["status"] = next((s for s in STATES if s in row_states), "complete")
        return result

    try:
        original = Path(run_dir).absolute()
        if any(path.is_symlink() for path in (original,) + tuple(original.parents)):
            raise ValueError("run path must not traverse a symlink")
        base = original.resolve()
        run = read_object(safe_path(base, "run.json"))
        if run.get("schema_version") != 1 or type(run.get("schema_version")) is not int:
            raise ValueError("run schema_version must be 1")
        if any(not nonblank(run.get(k)) for k in ("run_id", "topic", "package", "source_cutoff")):
            raise ValueError("run requires run_id, topic, package and source_cutoff")
        if run.get("input_mode") not in ("topic", "research", "draft"):
            raise ValueError("invalid input_mode")
        date.fromisoformat(run["source_cutoff"])
        profile_path = safe_path(base, run.get("preset_path"))
        if digest(profile_path) != run.get("preset_sha256"):
            raise ValueError("profile snapshot hash differs from run.json")
        profile = read_object(profile_path)
        delivery_path = safe_path(base, run.get("delivery_manifest"))
        delivery = read_object(delivery_path)
        manifest_path = safe_path(base, run.get("core_manifest"))
        if manifest_path.parent != base:
            raise ValueError("core manifest must be in the run root so all artifact paths share one base")
        engine_root = safe_path(base, run.get("engine_dir"))
        if profile.get("schema_version") != 1 or type(profile.get("schema_version")) is not int:
            raise ValueError("profile schema_version must be 1")
        if delivery.get("schema_version") != 1 or type(delivery.get("schema_version")) is not int:
            raise ValueError("delivery schema_version must be 1")
        packages, descriptors = profile.get("packages"), profile.get("deliverables")
        if not isinstance(packages, dict) or not isinstance(descriptors, dict):
            raise ValueError("profile requires packages and deliverables objects")
        required = packages.get(run["package"])
        if (not isinstance(required, list) or not required or any(not nonblank(x) for x in required)
                or len(required) != len(set(required))):
            raise ValueError("selected package must contain unique nonempty role IDs")
        for role in required:
            descriptor = descriptors.get(role)
            if not isinstance(descriptor, dict) or descriptor.get("format") not in ("txt", "html", "md", "json", "pdf", "docx", "zip", "mp3", "mp4"):
                raise ValueError("missing deliverable descriptor for " + role)
            checks = descriptor.get("checks")
            if (not isinstance(checks, list) or not checks or any(not nonblank(x) for x in checks)
                    or len(checks) != len(set(checks))):
                raise ValueError("descriptor requires unique nonempty check kinds: " + role)
            if descriptor.get("canonical_language") not in (None, "zh", "en"):
                raise ValueError("invalid canonical language for " + role)
            providers = descriptor.get("allowed_providers")
            if providers is not None and (not isinstance(providers, list) or not providers
                    or any(not nonblank(value) for value in providers) or len(providers) != len(set(providers))):
                raise ValueError("allowed_providers must be a nonempty string list for " + role)
            target = descriptor.get("target")
            if target is not None and (not isinstance(target, dict) or target.get("metric") not in ("rendered_pages", "duration_seconds", "body_Han_characters", "body_words")
                    or any(not number(target.get(k)) for k in ("min", "max"))
                    or target["min"] < 0 or target["max"] < target["min"]
                    or target.get("enforcement") not in ("advisory", "required")):
                raise ValueError("invalid target for " + role)
            if target:
                metric = target["metric"]
                required_measurement = {"rendered_pages": {"document_render", "rendered_pages"},
                                        "duration_seconds": {"media_duration", "duration_seconds"}}.get(metric)
                if required_measurement and not required_measurement.intersection(checks):
                    raise ValueError("target requires a matching measurement check for " + role)
                language = {"body_Han_characters": "zh", "body_words": "en"}.get(metric)
                if language and descriptor.get("canonical_language") != language:
                    raise ValueError("body target requires matching canonical_language for " + role)
        result["run_id"], result["package"] = run["run_id"], run["package"]
    except (OSError, ValueError, TypeError, KeyError) as exc:
        issue("run_schema", str(exc))
        return finish()

    canonical, core_reviews, article_writers, engine_ok = {}, [], set(), False
    try:
        lock = load_lock()
        result["engine"] = verify_engine(engine_root, lock)
        if run.get("engine") != {key: lock[key] for key in ("name", "version", "repository", "commit")}:
            raise ValueError("Declared run engine differs from the verified lock")
        engine_ok = True
    except (OSError, ValueError, TypeError, KeyError) as exc:
        issue("engine_integrity", str(exc), "blocked")
    try:
        core_manifest = read_object(manifest_path)
        if type(core_manifest.get("schema_version")) is not int or core_manifest["schema_version"] != 2:
            raise ValueError("This release requires a schema-2 core manifest for criterion-level and fresh final reviews")
        if not isinstance(core_manifest.get("reviews"), list):
            raise ValueError("core manifest reviews must be a list")
        core_reviews = core_manifest["reviews"]
        if nonblank(core_manifest.get("integrator_id")):
            article_writers.add(core_manifest["integrator_id"])
        artifacts = core_manifest.get("artifacts")
        if not isinstance(artifacts, list) or any(not isinstance(x, dict) for x in artifacts):
            raise ValueError("core manifest artifacts must be objects")
        core_ids, core_paths = set(), set()
        for artifact in artifacts:
            identifier = artifact.get("id")
            if not nonblank(identifier) or identifier in core_ids:
                raise ValueError("core artifacts require unique IDs")
            core_ids.add(identifier)
            artifact_path = safe_path(base, artifact.get("path"))
            if artifact_path in core_paths:
                raise ValueError("core artifacts require unique paths")
            core_paths.add(artifact_path)
            if artifact.get("kind") == "article":
                canonical[identifier] = artifact
                if nonblank(artifact.get("author_id")):
                    article_writers.add(artifact["author_id"])
                validate_article_criteria(artifact)
        for claim in core_manifest.get("claims", []):
            if not isinstance(claim, dict) or not isinstance(claim.get("occurrences"), list):
                raise ValueError("invalid core claim occurrence declarations")
            for occurrence in claim["occurrences"]:
                if not isinstance(occurrence, dict):
                    raise ValueError("invalid core claim occurrence")
                safe_path(base, occurrence.get("path"))
        if not core_manifest.get("sources") or not core_manifest.get("claims"):
            issue("evidence_inventory", "Factual packages require nonempty source and claim inventories.", "incomplete")
        if engine_ok:
            script = engine_root / "skills/evidence-to-article/scripts/check_run.py"
            environment = os.environ.copy()
            environment.pop("PYTHONPATH", None)
            environment.pop("PYTHONHOME", None)
            proc = subprocess.run([sys.executable, "-B", "-E", "-s", str(script), "--manifest", str(manifest_path)],
                                  cwd=str(script.parent), env=environment, capture_output=True,
                                  text=True, timeout=45)
            core_report = json.loads(proc.stdout)
            if not isinstance(core_report, dict) or type(core_report.get("ok")) is not bool:
                raise ValueError("core checker returned an invalid report")
            result["core_audit"] = core_report
            result["core_audit"]["execution"] = "fresh_locked_subprocess"
            if proc.returncode != 0 or not core_report["ok"]:
                issue("core_audit", "Evidence to Article did not pass; inspect core_audit.errors.",
                      "incomplete" if not canonical else "changes_required")
            for warning in core_report.get("warnings", []):
                issue("core_warning", str(warning.get("message", warning)) if isinstance(warning, dict) else str(warning), warning=True)
    except (OSError, ValueError, TypeError, KeyError, subprocess.TimeoutExpired) as exc:
        issue("core_manifest", str(exc), "incomplete" if not manifest_path.is_file() else "changes_required")

    items = delivery.get("items")
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        issue("delivery_schema", "delivery.items must be an array of objects")
        return finish()
    indexed, occupied, hashes, inspections = {}, {}, {}, {}
    for item in items:
        role = item.get("role")
        if not nonblank(role) or role in indexed:
            issue("delivery_schema", "items require unique nonempty roles")
            continue
        indexed[role] = item
        if role not in required:
            issue("unexpected_role", "Role is outside the selected package: " + role, role=role)
    for role in required:
        item = indexed.get(role)
        row = {"role": role, "status": "incomplete"}
        items_report.append(row)
        if item is None:
            issue("missing_output", "Required output has no delivery record.", "incomplete", role)
            continue
        row["declared_status"] = item.get("status")
        row["path"] = item.get("path")
        declared = item.get("status")
        if declared not in ("pending", "blocked", "complete"):
            issue("item_status", "Allowed item statuses: pending, blocked, complete.", role=role)
        elif declared == "pending":
            issue("pending_output", "Output remains pending.", "incomplete", role)
        elif declared == "blocked":
            issue("blocked_output", item.get("reason") if nonblank(item.get("reason")) else "Blocked output requires a concrete reason.", "blocked", role)
        try:
            path = safe_path(base, item.get("path"))
            if path in occupied:
                raise ValueError("output path is already assigned to " + occupied[path])
            occupied[path] = role
            if not path.is_file():
                issue("missing_file", "Required output file is missing.", "incomplete", role)
                continue
            hashes[role] = digest(path)
            row["actual_sha256"] = hashes[role]
            if declared == "complete":
                if not isinstance(item.get("sha256"), str) or not DIGEST.fullmatch(item["sha256"]):
                    issue("item_hash", "Complete output requires its lowercase SHA-256.", role=role)
                elif item["sha256"] != hashes[role]:
                    issue("item_hash", "Recorded output hash is stale.", role=role)
                if not nonblank(item.get("author_id")):
                    issue("item_author", "Complete output requires its real author/producer identity.", role=role)
            inspections[role] = inspect_file(path, descriptors[role]["format"])
            row["format_check"] = inspections[role]
        except (OSError, ValueError, TypeError, KeyError, zipfile.BadZipFile, subprocess.TimeoutExpired) as exc:
            issue("file_format", str(exc), role=role)

    # Keep the same specialist's remit across languages, adaptations and media.
    editorial_assignments = {}
    reviewer_types = {}
    for review in core_reviews:
        if (isinstance(review, dict) and nonblank(review.get("reviewer_id")) and
                nonblank(review.get("criterion")) and review.get("reviewer_type") in ("agent", "human")):
            editorial_assignments[review["reviewer_id"]] = review["criterion"]
            reviewer_types[review["reviewer_id"]] = review["reviewer_type"]
    check_criteria = {criterion: criterion for criterion in editorial_assignments.values() if criterion != "holistic"}
    check_criteria.update(readability="readability", source_review="source_meaning")
    for role in required:
        item = indexed.get(role)
        if item is None or item.get("status") != "complete":
            continue
        descriptor = descriptors[role]
        if descriptor.get("allowed_providers") and item.get("provider") not in descriptor["allowed_providers"]:
            issue("media_provider", "Actual provider must match the selected preset and have provenance evidence.", role=role)
        language = descriptor.get("canonical_language")
        origin = canonical.get(item.get("canonical_id")) if isinstance(item.get("canonical_id"), str) else None
        origin_hash = None
        if language:
            if not origin or origin.get("language") != language:
                issue("canonical_binding", "Output must reference an audited canonical article in " + language + ".", role=role)
            else:
                try:
                    origin_hash = digest(safe_path(base, origin.get("path")))
                    if origin_hash != origin.get("sha256"):
                        issue("canonical_binding", "Canonical article hash is stale.", role=role)
                    if item.get("author_id") != origin.get("author_id"):
                        issue("canonical_author", "Output author must match its canonical author.", role=role)
                except (OSError, ValueError, TypeError) as exc:
                    issue("canonical_binding", str(exc), role=role)
        checks = item.get("checks")
        if not isinstance(checks, list) or any(not isinstance(c, dict) for c in checks):
            issue("check_schema", "checks must be a list of actual review records.", role=role)
            continue
        indexed_checks = {}
        for check in checks:
            kind = check.get("kind")
            if not nonblank(kind) or kind in indexed_checks:
                issue("check_schema", "Check kinds must be unique nonempty strings.", role=role)
                continue
            indexed_checks[kind] = check
        for kind in descriptor["checks"] + [name for name in indexed_checks if name not in descriptor["checks"]]:
            check = indexed_checks.get(kind)
            if not check or check.get("status") == "not_run":
                if kind in descriptor["checks"]:
                    issue("missing_check", kind + " has not been performed.", "incomplete", role)
                continue
            if check.get("status") not in ("pass", "fail"):
                issue("check_schema", kind + " has an invalid status.", role=role)
                continue
            if check["status"] == "fail":
                issue("failed_check", kind + " reports a failure.", role=role)
            if any(not nonblank(check.get(k)) for k in ("reviewer_id", "evidence")) or not valid_stamp(check.get("reviewed_at")):
                issue("check_attestation", kind + " needs reviewer, evidence and a timezone-qualified timestamp.", role=role)
            reviewer = check.get("reviewer_id")
            if nonblank(reviewer) and reviewer != reviewer.strip():
                issue("reviewer_id", kind + " reviewer identity must have no surrounding whitespace.", role=role)
            reviewer_type = check.get("reviewer_type")
            if reviewer_type not in ("agent", "human", "tool"):
                issue("reviewer_type", kind + " needs the actual reviewer type (agent, human or tool).", role=role)
            criterion = check_criteria.get(kind, "delivery")
            if reviewer_type == "tool" and kind in ("source_review", "readability", "full_listening", "full_playback"):
                issue("reviewer_type", kind + " requires an agent or human who performed the review.", role=role)
            if nonblank(reviewer):
                if reviewer in reviewer_types and reviewer_types[reviewer] != reviewer_type:
                    issue("reviewer_type", reviewer + " has inconsistent reviewer types in this run.", role=role)
                reviewer_types[reviewer] = reviewer_type
                previous = editorial_assignments.setdefault(reviewer, criterion)
                if previous != criterion:
                    issue("reviewer_independence", kind + " needs a reviewer independent of " + previous + ".", role=role)
            if nonblank(reviewer) and (reviewer == item.get("author_id") or reviewer in article_writers):
                issue("self_review", kind + " needs a reviewer independent of the editorial writers and item producer.", role=role)
            if check.get("artifact_sha256") != hashes.get(role) or role not in hashes:
                issue("stale_check", kind + " is not bound to the current output bytes.", role=role)
            related = check.get("related_hashes", {})
            if not isinstance(related, dict):
                issue("check_schema", kind + " related_hashes must be an object.", role=role)
                related = {}
            for related_role, related_hash in related.items():
                expected = origin_hash if related_role == "canonical" else hashes.get(related_role)
                if expected is None or related_hash != expected:
                    issue("stale_related", kind + " has a missing or stale related hash: " + str(related_role), role=role)
            if kind == "output_consistency" and (origin_hash is None or related.get("canonical") != origin_hash):
                issue("canonical_consistency", "Output consistency must bind the current canonical article.", role=role)
            audio_bound = kind in ("transcript_alignment", "storyboard_timing", "storyboard", "video_sync")
            audio_bound = audio_bound or (kind == "audio_content" and "transcript" in role)
            if audio_bound and ("audio_mp3" not in hashes or related.get("audio_mp3") != hashes["audio_mp3"]):
                issue("media_alignment", kind + " must bind the current audio_mp3 hash.", role=role)
        target = descriptor.get("target")
        if target:
            metric = target["metric"]
            value = None
            if metric.lower() in ("han_characters", "body_han_characters", "han_body", "body_words"):
                core_counts = (result.get("core_audit") or {}).get("body_counts", {})
                count = core_counts.get(item.get("canonical_id"), {})
                expected_language = "en" if metric.lower() == "body_words" else "zh"
                expected_unit = "English words" if expected_language == "en" else "Han characters"
                if language == expected_language and count.get("unit") == expected_unit:
                    value = count.get("count")
            else:
                candidates = {"rendered_pages": ("document_render", "rendered_pages"),
                              "duration_seconds": ("media_duration", "duration_seconds")}.get(metric, (metric,))
                for name in candidates:
                    if indexed_checks.get(name, {}).get("status") == "pass":
                        value = indexed_checks[name].get("measured_value")
                        break
            if not number(value):
                issue("target_measurement", "No valid measurement for " + metric + ".", "incomplete", role)
            elif metric == "rendered_pages" and (value <= 0 or int(value) != value):
                issue("target_measurement", "Rendered pages must be a positive integer.", role=role)
            elif metric == "duration_seconds" and value <= 0:
                issue("target_measurement", "Media duration must be positive.", role=role)
            else:
                next(row for row in items_report if row["role"] == role)["measurement"] = {"metric": metric, "value": value}
                if not target["min"] <= value <= target["max"]:
                    issue("target_range", f"{metric} {value} is outside {target['min']}–{target['max']}.",
                          role=role, warning=target["enforcement"] == "advisory")
                actual_duration = inspections.get(role, {}).get("duration_seconds")
                if metric == "duration_seconds" and actual_duration is not None and abs(actual_duration - value) > 1.5:
                    issue("duration_mismatch", "Declared duration differs from ffprobe measurement.", role=role)

    approval = delivery.get("approval")
    if not isinstance(approval, dict) or type(approval.get("required")) is not bool:
        issue("approval_schema", "approval requires a boolean required field.")
    elif approval["required"] or approval.get("status") == "approved":
        valid = (approval.get("status") == "approved" and nonblank(approval.get("reviewer_id"))
                 and nonblank(approval.get("evidence")) and isinstance(approval.get("package_hashes"), dict)
                 and set(approval["package_hashes"]) == set(required)
                 and all(role in hashes and approval["package_hashes"][role] == hashes[role] for role in required))
        if not valid:
            issue("approval_pending" if approval["required"] else "approval_schema",
                  "Approval is absent, incomplete or bound to old package bytes.",
                  "approval_pending" if approval["required"] else "changes_required")
    elif approval.get("status") not in ("not_requested", "not_required"):
        issue("approval_schema", "Unrequired approval status must be not_requested, not_required or a valid approved record.")
    return finish()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = audit(args.run_dir)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        report = {"schema_version": 1, "ok": False, "status": "changes_required",
                  "semantic_verification_performed": False, "scope": SCOPE,
                  "issues": [{"code": "invalid_input", "message": str(exc), "severity": "error"}],
                  "error_count": 1, "warning_count": 0}
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        try:
            output = args.report.absolute()
            if output.exists() or output.is_symlink():
                raise ValueError("report path already exists; use a new report filename")
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("x", encoding="utf-8") as stream:
                stream.write(rendered)
        except (OSError, ValueError) as exc:
            print(json.dumps({"ok": False, "status": "changes_required", "error": str(exc)}))
            return 1
    print(rendered, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
