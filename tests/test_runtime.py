"""CLI integration tests using a pinned, locally supplied Evidence to Article core.

All source/read/review/provider declarations below are SYNTHETIC SOFTWARE TEST
RECORDS. They are deliberately constructed to test the acceptance contract, not
evidence of source reading, editorial quality, listening or provider generation.

Run with EVIDENCE_ENGINE_SOURCE pointing to a verified repository-layout cache.
PLAYBOOK_SKILL_DIR optionally selects a skill checkout instead of this repository.
No tests fetch external sources, publish files or invoke a paid media service.
"""

import copy
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = Path(os.environ.get("PLAYBOOK_SKILL_DIR", ROOT / "skills" / "editorial-playbook"))
SOURCE_ENV = os.environ.get("EVIDENCE_ENGINE_SOURCE")
SOURCE = Path(SOURCE_ENV).resolve() if SOURCE_ENV else None
STAMP = "2026-11-17T12:00:00+00:00"
TEST_EVIDENCE = "SYNTHETIC SOFTWARE TEST RECORD; no actual editorial review occurred."
# A short silent MP3 created locally with FFmpeg/libmp3lame, not a service output.
SILENT_MP3 = base64.b64decode(
    'SUQzBAAAAAAAIlRTU0UAAAAOAAADTGF2ZjYxLjcuMTAzAAAAAAAAAAAAAAD/4xjEAAAAA0gAAAAATEFN'
    'RTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVX/4xjE'
    'OwAAA0gAAAAAVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV'
    'VVVVVVVVVVX/4xjEdgAAA0gAAAAAVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV'
    'VVVVVVVVVVVVVVVVVVVVVVVVVVX/4xjEsQAAA0gAAAAAVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV'
    'VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVU='
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def invoke(script, *args):
    result = subprocess.run(
        [sys.executable, "-B", str(script), *map(str, args)],
        text=True, capture_output=True, timeout=45,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    try:
        report = json.loads(result.stdout)
    except (ValueError, TypeError) as exc:
        raise AssertionError("CLI did not return JSON:\n" + result.stdout + "\n" + result.stderr) from exc
    return result.returncode, report


class RuntimeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if SOURCE is None or not SOURCE.is_dir():
            raise unittest.SkipTest("Set EVIDENCE_ENGINE_SOURCE to a verified repository-layout core cache")
        for filename in ("prepare_run.py", "check_delivery.py"):
            if not (SKILL / "scripts" / filename).is_file():
                raise unittest.SkipTest("Runtime script is unavailable: " + filename)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="playbook-contract-test-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.run = self.base / "run"
        self.preset_path = self.base / "synthetic-preset.json"
        self.profile = {
            "schema_version": 1,
            "id": "synthetic-software-test",
            "version": "1.0.0",
            "description": "Synthetic acceptance fixture, not an editorial demonstration",
            "packages": {"articles": ["blog_en"]},
            "deliverables": {
                "blog_en": {
                    "path": "outputs/Blog_EN_V1.txt", "format": "txt",
                    "canonical_language": "en",
                    "checks": ["output_consistency", "format_review"],
                },
            },
        }

    def prepare(self, profile=None, run=None, source=None, capabilities=None):
        write_json(self.preset_path, profile or self.profile)
        args = ["--run-dir", run or self.run, "--topic", "Synthetic notice", "--input-mode", "research",
                "--cutoff", "2026-11-17", "--preset", self.preset_path,
                "--engine-source", source or SOURCE, "--offline"]
        if capabilities is not None:
            path = self.base / "capabilities-input.json"
            write_json(path, capabilities)
            args.extend(["--capabilities", path])
        return invoke(SKILL / "scripts" / "prepare_run.py", *args)

    def check(self, run=None):
        return invoke(SKILL / "scripts" / "check_delivery.py", "--run-dir", run or self.run)

    def assertNotReady(self, result, contains=None):
        code, report = result
        self.assertNotEqual(code, 0, report)
        self.assertFalse(report.get("ok"), report)
        self.assertFalse(report.get("semantic_verification_performed", False), report)
        self.assertNotEqual(report.get("status"), "ready_for_handoff", report)
        if contains:
            self.assertIn(contains.lower(), json.dumps(report).lower())
        return report

    def assertReady(self):
        code, report = self.check()
        self.assertEqual(code, 0, report)
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["status"], "ready_for_handoff", report)
        self.assertIs(report["semantic_verification_performed"], False)
        return report

    def build_core_fixture(self):
        canonical = self.run / "article-en.md"
        canonical.write_text(
            "# Synthetic notice\n\nThe synthetic library opens at noon.\n\n"
            "## Sources\n\nSynthetic notice supplied for software testing.\n", encoding="utf-8")
        source = self.run / "evidence" / "synthetic-notice.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("SYNTHETIC: The synthetic library opens at noon.\n", encoding="utf-8")
        core = self.run / ".engine" / "skills" / "evidence-to-article"
        code, report = invoke(core / "scripts" / "build_outputs.py", "--input", canonical, "--out-dir", self.run / "audit")
        self.assertEqual(code, 0, report)
        article_hash = digest(canonical.read_bytes())
        artifacts = [{
            "id": "article-en", "kind": "article", "path": "article-en.md", "language": "en",
            "author_id": "synthetic-writer", "sha256": article_hash,
            "expected_body_count": {"min": 1, "max": 100},
        }]
        for kind in ("txt", "html"):
            path = self.run / "audit" / ("article-en." + kind)
            artifacts.append({"id": "audit-en-" + kind, "kind": kind,
                              "path": path.relative_to(self.run).as_posix(), "language": "en",
                              "author_id": "synthetic-writer", "sha256": digest(path.read_bytes()),
                              "canonical_id": "article-en"})
        manifest = {
            "schema_version": 1, "artifacts": artifacts,
            "sources": [{"id": "s1", "locator": "evidence/synthetic-notice.txt", "status": "read", "read_at": STAMP,
                         "note": TEST_EVIDENCE}],
            "claims": [{"id": "c1", "critical": True, "status": "support", "source_ids": ["s1"],
                        "occurrences": [{"path": "article-en.md", "language": "en",
                                         "quote": "The synthetic library opens at noon."}]}],
            "reviews": [{"id": "test-" + lane, "lane": lane, "reviewer_id": "synthetic-reviewer-" + lane,
                         "decision": "approve", "artifact_hashes": {"article-en": article_hash}, "findings": [],
                         "note": TEST_EVIDENCE} for lane in ("readability", "source", "overall")],
        }
        write_json(self.run / "core-manifest.json", manifest)
        return article_hash

    def complete_record(self, role, path, checks, canonical_id=None, related=None):
        file_hash = digest((self.run / path).read_bytes())
        return {
            "role": role, "path": path, "status": "complete", "sha256": file_hash,
            "author_id": "synthetic-writer", "canonical_id": canonical_id,
            "checks": [{"kind": kind, "status": "pass", "reviewer_id": "synthetic-reviewer-" + kind,
                        "reviewed_at": STAMP, "artifact_sha256": file_hash, "evidence": TEST_EVIDENCE,
                        "related_hashes": dict(related or {})} for kind in checks],
        }

    def complete_run(self, profile=None, assert_ready=True):
        code, report = self.prepare(profile=profile)
        self.assertEqual(code, 0, report)
        canonical_hash = self.build_core_fixture()
        target = self.run / "outputs" / "Blog_EN_V1.txt"
        target.parent.mkdir(exist_ok=True)
        target.write_bytes((self.run / "article-en.md").read_bytes())
        delivery = read_json(self.run / "delivery.json")
        delivery["items"][0] = self.complete_record(
            "blog_en", "outputs/Blog_EN_V1.txt", ["output_consistency", "format_review"],
            "article-en", {"canonical": canonical_hash})
        write_json(self.run / "delivery.json", delivery)
        if assert_ready:
            self.assertReady()
        return delivery

    def save_delivery(self, delivery):
        write_json(self.run / "delivery.json", delivery)

    def complete_media_run(self):
        profile = copy.deepcopy(self.profile)
        profile["packages"]["articles"].extend(["audio_mp3", "audio_transcript_en"])
        profile["deliverables"].update({
            "audio_mp3": {"path": "outputs/Audio_EN_V1.mp3", "format": "mp3",
                          "checks": ["provider_provenance", "audio_content", "full_listening"],
                          "allowed_providers": ["synthetic_test_provider"]},
            "audio_transcript_en": {"path": "outputs/Transcript_EN_V1.txt", "format": "txt",
                                    "checks": ["transcript_alignment", "source_review"]},
        })
        delivery = self.complete_run(profile, assert_ready=False)
        (self.run / "outputs/Audio_EN_V1.mp3").write_bytes(SILENT_MP3)
        (self.run / "outputs/Transcript_EN_V1.txt").write_text("Synthetic fixture: silence.\n", encoding="utf-8")
        audio = self.complete_record("audio_mp3", "outputs/Audio_EN_V1.mp3",
                                     profile["deliverables"]["audio_mp3"]["checks"])
        audio["provider"] = "synthetic_test_provider"
        transcript = self.complete_record("audio_transcript_en", "outputs/Transcript_EN_V1.txt",
                                          profile["deliverables"]["audio_transcript_en"]["checks"],
                                          related={"audio_mp3": audio["sha256"]})
        delivery["items"][1:] = [audio, transcript]
        self.save_delivery(delivery)
        self.assertReady()
        return delivery

    def complete_pdf_run(self, rendered_pages=None):
        profile = copy.deepcopy(self.profile)
        profile["packages"]["articles"].append("research_en")
        descriptor = {"path": "outputs/Research_EN_V1.pdf", "format": "pdf", "checks": ["source_review"]}
        if rendered_pages is not None:
            descriptor["checks"].append("document_render")
            descriptor["target"] = {"metric": "rendered_pages", "min": 1, "max": 3, "enforcement": "advisory"}
        profile["deliverables"]["research_en"] = descriptor
        delivery = self.complete_run(profile, assert_ready=False)
        # Deliberately only a signature fixture: the validator must not claim it rendered a PDF.
        path = self.run / descriptor["path"]
        path.write_bytes(b"%PDF-1.4\n% SYNTHETIC SOFTWARE TEST SIGNATURE FIXTURE\n%%EOF\n")
        record = self.complete_record("research_en", descriptor["path"], descriptor["checks"])
        if rendered_pages is not None:
            next(c for c in record["checks"] if c["kind"] == "document_render")["measured_value"] = rendered_pages
        delivery["items"][1:] = [record]
        self.save_delivery(delivery)
        self.assertReady()
        return delivery

    def update_profile(self, change):
        profile = read_json(self.run / "profile.json")
        change(profile)
        write_json(self.run / "profile.json", profile)
        run = read_json(self.run / "run.json")
        run["preset_sha256"] = digest((self.run / "profile.json").read_bytes())
        write_json(self.run / "run.json", run)

    def test_prepare_never_marks_empty_templates_complete(self):
        code, report = self.prepare()
        self.assertEqual(code, 0, report)
        self.assertEqual(report["status"], "prepared")
        delivery = read_json(self.run / "delivery.json")
        self.assertTrue(all(x["status"] == "pending" and not x["checks"] for x in delivery["items"]))
        self.assertEqual(read_json(self.run / "core-manifest.json")["reviews"], [])
        self.assertNotReady(self.check())

    def test_preflight_keeps_unobserved_capabilities_unknown(self):
        code, report = self.prepare()
        self.assertEqual(code, 0, report)
        values = read_json(self.run / "capabilities.json").values()
        self.assertTrue(all(x["status"] == "unknown" for x in values))
        self.assertIn("source_access", json.dumps(read_json(self.run / "preflight.json")))

    def test_existing_run_is_not_overwritten(self):
        self.run.mkdir()
        sentinel = self.run / "do-not-replace.txt"
        sentinel.write_text("existing work", encoding="utf-8")
        code, report = self.prepare()
        self.assertNotEqual(code, 0, report)
        self.assertEqual(sentinel.read_text(), "existing work")

    def test_changed_dependency_prevents_setup(self):
        source = self.base / "bad-core"
        shutil.copytree(SOURCE, source)
        script = source / "skills/evidence-to-article/scripts/check_run.py"
        script.write_text(script.read_text() + "\n# modified\n", encoding="utf-8")
        code, report = self.prepare(source=source)
        self.assertNotEqual(code, 0, report)
        self.assertFalse(self.run.exists(), report)

    def test_synthetic_contract_fixture_uses_real_core_and_can_pass(self):
        self.complete_run()
        report = self.assertReady()
        self.assertIn("core", json.dumps(report).lower())

    def test_changed_installed_core_blocks_check(self):
        self.complete_run()
        path = self.run / ".engine/skills/evidence-to-article/scripts/check_run.py"
        path.write_text(path.read_text() + "\n# modified\n", encoding="utf-8")
        self.assertNotReady(self.check())

    def test_missing_required_file_is_not_accepted(self):
        self.complete_run()
        (self.run / "outputs/Blog_EN_V1.txt").unlink()
        self.assertNotReady(self.check())

    def test_missing_required_role_is_not_accepted(self):
        delivery = self.complete_run()
        delivery["items"] = []
        self.save_delivery(delivery)
        self.assertNotReady(self.check())

    def test_unknown_status_is_not_treated_as_complete(self):
        delivery = self.complete_run()
        delivery["items"][0]["status"] = "approved"
        self.save_delivery(delivery)
        self.assertNotReady(self.check())

    def test_existing_file_without_checks_does_not_pass(self):
        delivery = self.complete_run()
        delivery["items"][0]["checks"] = []
        self.save_delivery(delivery)
        self.assertNotReady(self.check())

    def test_check_not_run_does_not_pass(self):
        delivery = self.complete_run()
        delivery["items"][0]["checks"][0]["status"] = "not_run"
        self.save_delivery(delivery)
        self.assertNotReady(self.check())

    def test_changed_output_invalidates_old_check_even_with_new_file_hash(self):
        delivery = self.complete_run()
        path = self.run / "outputs/Blog_EN_V1.txt"
        path.write_bytes(path.read_bytes() + b"\nChanged output.\n")
        delivery["items"][0]["sha256"] = digest(path.read_bytes())
        self.save_delivery(delivery)
        self.assertNotReady(self.check())

    def test_stale_core_review_cannot_be_replaced_by_saved_report(self):
        self.complete_run()
        manifest = read_json(self.run / "core-manifest.json")
        manifest["reviews"][0]["artifact_hashes"]["article-en"] = "0" * 64
        write_json(self.run / "core-manifest.json", manifest)
        write_json(self.run / "core-report.json", {"ok": True, "errors": []})
        self.assertNotReady(self.check())

    def test_core_self_review_is_rejected(self):
        self.complete_run()
        manifest = read_json(self.run / "core-manifest.json")
        manifest["reviews"][0]["reviewer_id"] = "synthetic-writer"
        write_json(self.run / "core-manifest.json", manifest)
        self.assertNotReady(self.check())

    def test_missing_claim_inventory_blocks_publication_package(self):
        self.complete_run()
        manifest = read_json(self.run / "core-manifest.json")
        manifest["claims"] = []
        write_json(self.run / "core-manifest.json", manifest)
        self.assertNotReady(self.check())

    def test_unknown_canonical_is_rejected(self):
        delivery = self.complete_run()
        delivery["items"][0]["canonical_id"] = "no-such-article"
        self.save_delivery(delivery)
        self.assertNotReady(self.check())

    def test_wrong_canonical_language_is_rejected(self):
        self.complete_run()
        self.update_profile(lambda p: p["deliverables"]["blog_en"].update(canonical_language="zh"))
        self.assertNotReady(self.check())

    def test_required_profile_count_cannot_be_bypassed_by_relaxed_core_bounds(self):
        self.complete_run()
        self.update_profile(lambda p: p["deliverables"]["blog_en"].update(
            target={"metric": "body_words", "min": 40, "max": 50, "enforcement": "required"}))
        report = self.assertNotReady(self.check())
        self.assertIn("target_range", json.dumps(report))

    def test_advisory_profile_count_deviation_is_a_warning(self):
        self.complete_run()
        self.update_profile(lambda p: p["deliverables"]["blog_en"].update(
            target={"metric": "body_words", "min": 40, "max": 50, "enforcement": "advisory"}))
        report = self.assertReady()
        self.assertGreater(report["warning_count"], 0, report)

    def test_body_words_uses_actual_core_count_instead_of_declared_measurement(self):
        delivery = self.complete_run()
        self.update_profile(lambda p: p["deliverables"]["blog_en"].update(
            target={"metric": "body_words", "min": 6, "max": 6, "enforcement": "required"}))
        claimed_measurement = copy.deepcopy(delivery["items"][0]["checks"][1])
        claimed_measurement.update(kind="body_words", measured_value=999)
        delivery["items"][0]["checks"].append(claimed_measurement)
        self.save_delivery(delivery)
        report = self.assertReady()
        item = next(x for x in report["items"] if x["role"] == "blog_en")
        self.assertEqual(item["measurement"], {"metric": "body_words", "value": 6})

    def test_additional_measurement_check_still_requires_full_attestation(self):
        delivery = self.complete_run()
        delivery["items"][0]["checks"].append({"kind": "document_render", "status": "pass", "measured_value": 2})
        self.save_delivery(delivery)
        report = self.assertNotReady(self.check())
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("check_attestation", codes)
        self.assertIn("stale_check", codes)

    def test_pdf_custom_preset_uses_only_signature_inspection(self):
        self.complete_pdf_run()
        report = self.assertReady()
        item = next(x for x in report["items"] if x["role"] == "research_en")
        self.assertEqual(item["format_check"]["inspection"], "signature_only")
        self.assertIs(item["format_check"]["rendering_verified"], False)

    def test_rendered_pages_must_be_positive_integer_even_when_advisory(self):
        baseline = self.complete_pdf_run(rendered_pages=2)
        for value in (-1, 0, 0.5, 1.5):
            delivery = copy.deepcopy(baseline)
            record = next(x for x in delivery["items"] if x["role"] == "research_en")
            next(c for c in record["checks"] if c["kind"] == "document_render")["measured_value"] = value
            self.save_delivery(delivery)
            with self.subTest(rendered_pages=value):
                report = self.assertNotReady(self.check())
                self.assertIn("target_measurement", {issue["code"] for issue in report["issues"]})

    def test_unrecorded_profile_change_invalidates_snapshot_binding(self):
        self.complete_run()
        profile = read_json(self.run / "profile.json")
        profile["version"] = "2.0.0"
        write_json(self.run / "profile.json", profile)
        self.assertNotReady(self.check())

    def test_unavailable_audio_does_not_prevent_article_setup(self):
        code, report = self.prepare(capabilities={
            "audio_generation": {"status": "unavailable", "evidence": "Synthetic fixture: no audio service"}})
        self.assertEqual(code, 0, report)
        self.assertEqual(report["status"], "prepared")
        self.assertEqual(read_json(self.run / "capabilities.json")["audio_generation"]["status"], "unavailable")
        self.assertNotReady(self.check())

    def test_semantic_check_requires_independent_reviewer(self):
        delivery = self.complete_run()
        delivery["items"][0]["checks"][0]["reviewer_id"] = "synthetic-writer"
        self.save_delivery(delivery)
        self.assertNotReady(self.check())

    def test_check_requires_timezone_and_evidence(self):
        delivery = self.complete_run()
        for field, value in (("reviewed_at", "2026-11-17T12:00:00"), ("evidence", "")):
            changed = copy.deepcopy(delivery)
            changed["items"][0]["checks"][0][field] = value
            self.save_delivery(changed)
            with self.subTest(field=field):
                self.assertNotReady(self.check())

    def test_required_approval_has_separate_pending_status(self):
        delivery = self.complete_run()
        delivery["approval"] = {"required": True, "status": "pending", "reviewer_id": None, "evidence": None}
        self.save_delivery(delivery)
        report = self.assertNotReady(self.check())
        self.assertEqual(report["status"], "approval_pending", report)

    def test_unrequired_but_claimed_approval_cannot_omit_reviewer_or_hashes(self):
        delivery = self.complete_run()
        delivery["approval"] = {"required": False, "status": "approved", "reviewer_id": None, "evidence": None}
        self.save_delivery(delivery)
        report = self.assertNotReady(self.check())
        self.assertIn("approval_schema", {issue["code"] for issue in report["issues"]})

    def test_approval_is_bound_to_current_package(self):
        delivery = self.complete_run()
        delivery["approval"] = {"required": True, "status": "approved", "reviewer_id": "synthetic-approver",
                                "evidence": TEST_EVIDENCE, "package_hashes": {"blog_en": "0" * 64}}
        self.save_delivery(delivery)
        self.assertNotReady(self.check())
        delivery["approval"]["package_hashes"]["blog_en"] = delivery["items"][0]["sha256"]
        self.save_delivery(delivery)
        self.assertReady()

    def test_delivery_path_cannot_escape_run(self):
        delivery = self.complete_run()
        outside = self.base / "outside.txt"
        outside.write_bytes((self.run / "outputs/Blog_EN_V1.txt").read_bytes())
        delivery["items"][0]["path"] = "../outside.txt"
        self.save_delivery(delivery)
        self.assertNotReady(self.check())

    @unittest.skipUnless(hasattr(os, "symlink"), "Symlinks are unavailable")
    def test_delivery_symlink_is_rejected(self):
        self.complete_run()
        target = self.run / "outputs/Blog_EN_V1.txt"
        outside = self.base / "outside.txt"
        outside.write_bytes(target.read_bytes())
        target.unlink()
        target.symlink_to(outside)
        self.assertNotReady(self.check())

    def test_missing_full_listening_cannot_be_reported_as_finished_audio(self):
        delivery = self.complete_media_run()
        audio = delivery["items"][1]
        next(c for c in audio["checks"] if c["kind"] == "full_listening")["status"] = "not_run"
        self.save_delivery(delivery)
        self.assertNotReady(self.check())

    def test_audio_provider_must_match_selected_preset(self):
        delivery = self.complete_media_run()
        delivery["items"][1]["provider"] = "unselected_provider"
        self.save_delivery(delivery)
        self.assertNotReady(self.check())

    def test_audio_change_invalidates_transcript_even_if_audio_checks_renewed(self):
        delivery = self.complete_media_run()
        audio = delivery["items"][1]
        path = self.run / audio["path"]
        path.write_bytes(path.read_bytes() + b"\x00\x00")
        new_hash = digest(path.read_bytes())
        audio["sha256"] = new_hash
        for check in audio["checks"]:
            check["artifact_sha256"] = new_hash
        self.save_delivery(delivery)
        report = self.assertNotReady(self.check())
        self.assertIn("audio_mp3", json.dumps(report))

    def test_fake_mp3_extension_does_not_establish_audio_format(self):
        delivery = self.complete_media_run()
        audio = delivery["items"][1]
        path = self.run / audio["path"]
        path.write_bytes(b"This is plain text, not audio.")
        audio["sha256"] = digest(path.read_bytes())
        for check in audio["checks"]:
            check["artifact_sha256"] = audio["sha256"]
        for check in delivery["items"][2]["checks"]:
            check["related_hashes"]["audio_mp3"] = audio["sha256"]
        self.save_delivery(delivery)
        report = self.assertNotReady(self.check())
        self.assertIn("file_format", json.dumps(report))

    def test_blocked_output_is_reported_as_blocked(self):
        delivery = self.complete_run()
        delivery["items"][0]["status"] = "blocked"
        delivery["items"][0]["reason"] = "Synthetic fixture: required service unavailable"
        self.save_delivery(delivery)
        report = self.assertNotReady(self.check())
        self.assertEqual(report["status"], "blocked", report)


if __name__ == "__main__":
    unittest.main()
