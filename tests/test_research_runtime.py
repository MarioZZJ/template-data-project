"""Behavior tests using temporary checkouts; never submit real research or platform tasks."""
import argparse
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/research.py"
spec = importlib.util.spec_from_file_location("research", SCRIPT)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="research-runtime-test-", dir=os.environ.get("RESEARCH_TEST_TMPDIR"))
        self.base = Path(self.tmp.name)
        self.repo = self.base / "checkout"
        # Reuse existing committed history; tests do not create commits or change identity policy.
        subprocess.run(["git", "clone", "--quiet", "--shared", str(SCRIPT.parents[1]), str(self.repo)], check=True)
        r.git(self.repo, "remote", "set-url", "origin", "https://example.test/research/demo.git")
        self.assets = self.base / "ResearchAssets"

    def tearDown(self):
        # Remove only tasks created under this test's isolated asset root.
        for path in self.assets.glob("*/runs/*/run.json"):
            record = r.read_json(path)
            kind, identifier = record["supervisor"]["kind"], record["supervisor"]["id"]
            if kind == "windows" and os.name == "nt":
                subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", f"Unregister-ScheduledTask -TaskName {r.psquote(identifier)} -Confirm:$false -ErrorAction SilentlyContinue"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif kind == "launchd" and sys.platform == "darwin":
                subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/{identifier}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.tmp.cleanup()

    def args(self, *argv):
        return r.parser().parse_args(["--repo", str(self.repo), "--assets-home", str(self.assets), *argv])

    def setup(self):
        return r.setup(self.args("setup", "--stdlib"))

    def run_script(self, source, *options):
        return r.run(self.args("run", "--foreground", *options, "--", "python", "-c", source))

    def test_mapping_shared_origin_and_origin_rename(self):
        first = self.setup()
        other = self.base / "other-checkout"
        subprocess.run(["git", "clone", "--quiet", "--shared", str(self.repo), str(other)], check=True)
        r.git(other, "remote", "set-url", "origin", "git@example.test:research/demo.git")
        args = self.args("setup", "--stdlib")
        args.repo = str(other)
        self.assertEqual(r.setup(args)["asset_root"], first["asset_root"])
        r.git(self.repo, "remote", "set-url", "origin", "https://example.test/research/new-name.git")
        self.assertEqual(self.setup()["asset_root"], first["asset_root"])

    def test_same_name_different_origin_requires_alias(self):
        self.setup()
        other = self.base / "other"
        subprocess.run(["git", "clone", "--quiet", "--shared", str(self.repo), str(other)], check=True)
        r.git(other, "remote", "set-url", "origin", "https://different.test/demo.git")
        args = self.args("setup", "--stdlib")
        args.repo = str(other)
        with self.assertRaisesRegex(ValueError, "different origin"):
            r.setup(args)
        args.project_name = "other-demo"
        self.assertTrue(r.setup(args)["asset_root"].endswith("other-demo"))

    def test_no_origin_needs_explicit_name(self):
        r.git(self.repo, "remote", "remove", "origin")
        with self.assertRaises(ValueError):
            self.setup()
        result = r.setup(self.args("setup", "--stdlib", "--project-name", "paper-demo"))
        self.assertTrue(result["asset_root"].endswith("paper-demo"))

    def test_dirty_code_is_not_silently_omitted(self):
        self.setup()
        (self.repo / "new_scientific_script.py").write_text("print(1)")
        with self.assertRaisesRegex(ValueError, "Commit"):
            self.run_script("print(1)")

    def test_failure_has_terminal_evidence_and_never_reexecutes(self):
        self.setup()
        result = self.run_script("raise SystemExit(9)")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["exit_code"], 9)
        self.assertIsNotNone(result["finished_at"])
        before = dict(result)
        r.worker(Path(result["code_dir"]).parent / "run.json")
        self.assertEqual(before, r.read_json(Path(result["code_dir"]).parent / "run.json"))

    def test_outputs_are_isolated_inputs_and_environment_are_shared(self):
        info = self.setup()
        root = Path(info["asset_root"])
        fixed = root / "inputs/source.csv"
        fixed.write_text("x\n1\n")
        source = "import os,pathlib; pathlib.Path(os.environ['OUTPUT_ROOT'],'result.txt').write_text(pathlib.Path(os.environ['DATA_ROOT'],'source.csv').read_text())"
        first = self.run_script(source, "--input", f"source={fixed}")
        second = self.run_script(source, "--input", f"source={fixed}")
        self.assertEqual(first["status"], "succeeded")
        self.assertNotEqual(first["artifacts"][0]["path"], second["artifacts"][0]["path"])
        self.assertEqual(first["environment_dir"], second["environment_dir"])
        self.assertEqual(first["inputs"], second["inputs"])

    def test_input_mutation_is_failure_not_success(self):
        root = Path(self.setup()["asset_root"])
        fixed = root / "inputs/source.txt"
        fixed.write_text("fixed")
        result = self.run_script("import os,pathlib; pathlib.Path(os.environ['DATA_ROOT'],'source.txt').write_text('changed')", "--input", f"source={fixed}")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["failure_reason"], "fixed_input_modified")

    def test_deadline_stops_process_tree_without_retry(self):
        self.setup()
        deadline = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=1)).isoformat()
        result = self.run_script("import time; time.sleep(60)", "--deadline", deadline, "--attempt-limit", "2", "--budget-json", '{"approved_cost":1}')
        self.assertEqual(result["failure_reason"], "deadline_exceeded")
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(result["attempt_limit"], 2)
        self.assertEqual(result["budgets"], {"approved_cost": 1})

    def test_credentials_only_in_child_environment(self):
        root = Path(self.setup()["asset_root"])
        (root / ".env").write_text("TEST_PRIVATE_VALUE=do-not-record\nMULTICA_TOKEN=never-pass-to-job\n")
        result = self.run_script("import os; assert len(os.environ['TEST_PRIVATE_VALUE'])==13; assert 'MULTICA_TOKEN' not in os.environ")
        self.assertEqual(result["status"], "succeeded")
        self.assertNotIn("do-not-record", json.dumps(result))
        self.assertNotIn("never-pass-to-job", json.dumps(result))

    def test_delivery_without_calculation_requires_full_checks(self):
        self.setup()
        artifact = self.repo / "README.md"
        common = ["deliver", "--issue-id", "00000000-0000-0000-0000-000000000123", "--artifact", str(artifact), "--check", "reviewed full document", "--research-impact", "Clarifies interpretation"]
        with self.assertRaisesRegex(ValueError, "scope-complete"):
            r.deliver(self.args(*common))
        result = r.deliver(self.args(*common, "--scope-complete"))
        self.assertIsNone(result["record"]["run_id"])
        self.assertNotIn("source_task_id", result["record"])
        self.assertNotIn("comment_id", result["record"])
        stable = Path(result["record"]["artifacts"][0]["path"])
        self.assertNotEqual(stable, artifact)
        artifact.unlink()
        self.assertEqual(r.digest(stable), result["record"]["artifacts"][0]["sha256"])
        with self.assertRaisesRegex(ValueError, "review-evidence"):
            r.deliver(self.args(*common, "--scope-complete", "--review-required"))

    def test_export_acceptance_provenance_and_tamper_detection(self):
        self.setup()
        result = self.run_script("import os,pathlib; pathlib.Path(os.environ['OUTPUT_ROOT'],'table.csv').write_text('x,y\\n1,2\\n')")
        args = self.args("export", "--run-id", result["run_id"], "--file", "table.csv", "--kind", "tables", "--accepted-by", "phase acceptance comment")
        exported = r.export(args)
        self.assertEqual(exported["code_commit"], result["code_commit"])
        self.assertTrue((self.repo / "outputs/provenance.json").exists())
        with self.assertRaisesRegex(ValueError, "already exists"):
            r.export(args)
        args.replace = True
        Path(result["artifacts"][0]["path"]).write_text("tampered")
        with self.assertRaisesRegex(ValueError, "differs"):
            r.export(args)

    def test_dashboard_preserves_scientific_history(self):
        self.setup()
        dash = self.repo / "DASHBOARD.md"
        dash.write_text("# Scientific history\n\nOriginal conclusion.\n", encoding="utf-8")
        snap = self.base / "snapshot.json"
        r.atomic_json(snap, {"source_url": "https://multica.test/project", "generated_at": r.now(), "issues": [{"identifier": "DEMO-1", "title": "Research", "status": "in_review", "url": "https://multica.test/issue"}], "decisions": ["Choose phase scope"]})
        args = self.args("status", "--dashboard-from", str(snap))
        r.status(args)
        r.status(args)
        result = dash.read_text(encoding="utf-8")
        self.assertTrue(result.startswith("# Scientific history\n\nOriginal conclusion."))
        self.assertEqual(result.count("<!-- BEGIN MULTICA STATUS -->"), 1)
        self.assertIn("Choose phase scope", result)

    def test_concurrent_registry_updates_and_atomic_reads(self):
        env = os.environ.copy()
        commands = [sys.executable, str(SCRIPT), "--repo", str(self.repo), "--assets-home", str(self.assets), "setup", "--stdlib"]
        workers = [subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env) for _ in range(3)]
        for process in workers:
            out, err = process.communicate(timeout=30)
            self.assertEqual(process.returncode, 0, err.decode())
            self.assertIn("asset_root", json.loads(out))
        registry = r.read_json(self.assets / "projects.json")
        self.assertEqual(len(registry["projects"]), 1)

    def test_abandoned_recovery_never_restarts_or_resets_budget(self):
        self.setup()
        record = self.run_script("pass", "--attempt-limit", "2", "--budget-json", '{"limit":3}')
        path = Path(record["code_dir"]).parent / "run.json"
        record.update(status="running", finished_at=None, exit_code=None)
        record["created_at"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=2)).isoformat()
        r.atomic_json(path, record)
        with patch.object(r, "supervisor_active", return_value=False):
            result = r.reconcile_run(path)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["failure_reason"], "supervisor_ended_without_result")
        self.assertIsNone(result["exit_code"])
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(result["budgets"], {"limit": 3})
        r.worker(path)
        self.assertEqual(result, r.read_json(path))

    def test_uncertain_or_live_supervisor_is_not_marked_failed(self):
        self.setup()
        record = self.run_script("pass")
        path = Path(record["code_dir"]).parent / "run.json"
        record.update(status="running", finished_at=None)
        r.atomic_json(path, record)
        for active in (True, None):
            with patch.object(r, "supervisor_active", return_value=active):
                self.assertEqual(r.reconcile_run(path, grace_seconds=0)["status"], "running")
        with r.locked(path.parent / ".worker.lock"):
            with patch.object(r, "supervisor_active", return_value=False):
                self.assertEqual(r.reconcile_run(path, grace_seconds=0)["status"], "running")

    def test_nondefault_remote_ports_are_distinct_origins(self):
        values = []
        for remote in ("ssh://git@git.example.test:2222/team/paper.git", "ssh://git@git.example.test:2223/team/paper.git", "https://git.example.test:8443/team/paper.git"):
            r.git(self.repo, "remote", "set-url", "origin", remote)
            values.append(r.origin_identity(self.repo))
        self.assertEqual(len(set(values)), 3)

    def test_prepared_job_that_expires_never_starts_computation(self):
        self.setup()
        marker = self.base / "paid-submission-marker"
        record = self.run_script("pass")
        path = Path(record["code_dir"]).parent / "run.json"
        record.update(status="prepared", attempts=0, deadline=(dt.datetime.now(dt.timezone.utc)-dt.timedelta(seconds=1)).isoformat(), command=["python", "-c", f"import pathlib; pathlib.Path({str(marker)!r}).touch()"])
        r.atomic_json(path, record)
        r.worker(path)
        result = r.read_json(path)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["failure_reason"], "deadline_exceeded")
        self.assertFalse(marker.exists())

    def test_failed_input_verification_is_never_success(self):
        root = Path(self.setup()["asset_root"])
        fixed = root / "inputs/source.txt"
        fixed.write_text("fixed")
        original = r.digest
        calls = [0]
        def fail_after_command(path):
            if Path(path) == fixed:
                calls[0] += 1
                if calls[0] >= 3:
                    raise PermissionError("synthetic unreadable input")
            return original(path)
        with patch.object(r, "digest", side_effect=fail_after_command):
            result = self.run_script("pass", "--input", f"source={fixed}")
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["exit_code"], 0)
        self.assertIn("PermissionError", result["failure_reason"])
        self.assertTrue(result["finished_at"])

    def test_unreadable_output_still_has_terminal_failure(self):
        self.setup()
        original = r.digest
        def fail_on_output(path):
            if Path(path).name == "result.txt":
                raise PermissionError("synthetic unreadable output")
            return original(path)
        with patch.object(r, "digest", side_effect=fail_on_output):
            result = self.run_script("import os,pathlib; pathlib.Path(os.environ['OUTPUT_ROOT'],'result.txt').write_text('result')")
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["finished_at"])
        self.assertIn("artifact_evidence_error", result["failure_reason"])

    def test_export_failed_index_install_restores_both_files(self):
        self.setup()
        record = self.run_script("import os,pathlib; pathlib.Path(os.environ['OUTPUT_ROOT'],'table.csv').write_text('result')")
        args = self.args("export", "--run-id", record["run_id"], "--file", "table.csv", "--kind", "tables", "--accepted-by", "accepted")
        r.export(args)
        target = self.repo / "outputs/tables/table.csv"
        index = self.repo / "outputs/provenance.json"
        old_target, old_index = target.read_bytes(), index.read_bytes()
        args.replace = True
        original = os.replace
        def fail_index(source, dest):
            if Path(source).name.startswith(".export-index-") and Path(dest) == index:
                raise OSError("synthetic install failure")
            return original(source, dest)
        with patch.object(os, "replace", side_effect=fail_index):
            with self.assertRaisesRegex(OSError, "install failure"):
                r.export(args)
        self.assertEqual(target.read_bytes(), old_target)
        self.assertEqual(index.read_bytes(), old_index)

    @unittest.skipIf(os.name == "nt", "Symlink creation may need Windows developer mode")
    def test_export_rejects_symlink_escape(self):
        self.setup()
        record = self.run_script("import os,pathlib; pathlib.Path(os.environ['OUTPUT_ROOT'],'table.csv').write_text('result')")
        directory = self.repo / "outputs/tables"
        if directory.exists():
            shutil.rmtree(directory)
        outside = self.base / "outside"
        outside.mkdir()
        directory.symlink_to(outside, target_is_directory=True)
        args = self.args("export", "--run-id", record["run_id"], "--file", "table.csv", "--kind", "tables", "--accepted-by", "accepted")
        with self.assertRaisesRegex(ValueError, "symlink"):
            r.export(args)
        self.assertFalse((outside / "table.csv").exists())

    def test_export_rejects_copy_changed_after_source_check(self):
        self.setup()
        record = self.run_script("import os,pathlib; pathlib.Path(os.environ['OUTPUT_ROOT'],'table.csv').write_text('result')")
        source = Path(record["artifacts"][0]["path"])
        args = self.args("export", "--run-id", record["run_id"], "--file", "table.csv", "--kind", "tables", "--accepted-by", "accepted")
        original = shutil.copy2
        def changed_copy(src, dest, *a, **kw):
            result = original(src, dest, *a, **kw)
            if Path(src) == source:
                Path(dest).write_text("unaccepted concurrent bytes")
            return result
        with patch.object(shutil, "copy2", side_effect=changed_copy):
            with self.assertRaisesRegex(ValueError, "changed during export"):
                r.export(args)
        self.assertFalse((self.repo / "outputs/tables/table.csv").exists())
        self.assertFalse((self.repo / "outputs/provenance.json").exists())

    def test_foreign_worktree_crash_journal_does_not_block_export(self):
        self.setup()
        record = self.run_script("import os,pathlib; pathlib.Path(os.environ['OUTPUT_ROOT'],'table.csv').write_text('result')")
        args = self.args("export", "--run-id", record["run_id"], "--file", "table.csv", "--kind", "tables", "--accepted-by", "accepted")
        r.export(args)
        args.replace = True
        original = os.replace
        def fail_index(source, dest):
            if Path(source).name.startswith(".export-index-") and Path(dest).name == "provenance.json":
                raise OSError("simulated crash during commit")
            return original(source, dest)
        with patch.object(os, "replace", side_effect=fail_index), patch.object(r, "recover_export", side_effect=SystemExit("process died")):
            with self.assertRaises(SystemExit):
                r.export(args)
        other = self.base / "other-worktree"
        r.git(self.repo, "worktree", "add", "--quiet", "--detach", str(other))
        args.repo = str(other)
        args.replace = False
        exported = r.export(args)
        self.assertEqual(exported["sha256"], record["artifacts"][0]["sha256"])
        self.assertTrue((other / "outputs/provenance.json").is_file())

    def test_delivery_revision_anchor_and_attachment_filename(self):
        self.setup()
        result = r.deliver(self.args("deliver", "--issue-id", "00000000-0000-0000-0000-000000000123", "--artifact", str(self.repo / "README.md"), "--scope-complete", "--check", "full scope", "--research-impact", "documented", "--issue-revision", "7"))
        self.assertEqual(result["record"]["issue_revision"], 7)
        self.assertTrue(Path(result["delivery_path"]).name.startswith("research-delivery-"))

    def test_native_adapters_do_not_schedule_repeated_research(self):
        self.setup()
        record = self.run_script("pass")
        path = Path(record["code_dir"]).parent / "run.json"
        with patch.object(r, "call") as mocked:
            record["supervisor"]["kind"] = "systemd"
            r.launch(record, path)
            self.assertIn("--property=Restart=no", mocked.call_args.args[0])
            record["supervisor"]["kind"] = "windows"
            r.launch(record, path)
            script = mocked.call_args.args[0][-1]
            self.assertIn("IgnoreNew", script)
            self.assertNotIn("New-ScheduledTaskTrigger", script)
            record["supervisor"]["kind"] = "launchd"
            with patch.object(os, "getuid", return_value=501, create=True):
                r.launch(record, path)
            with (path.parent / "supervisor.plist").open("rb") as handle:
                self.assertFalse(r.plistlib.load(handle)["KeepAlive"])

    @unittest.skipUnless(os.environ.get("RESEARCH_NATIVE_TEST") == "1", "Set RESEARCH_NATIVE_TEST=1 on a real logged-in supported OS")
    def test_native_two_worktrees_share_input_with_isolated_parallel_outputs(self):
        root = Path(self.setup()["asset_root"])
        source = root / "inputs/fixed.txt"
        source.write_text("fixed input")
        records = []
        for number in range(2):
            tree = self.base / f"parallel-{number}"
            r.git(self.repo, "worktree", "add", "--quiet", "--detach", str(tree))
            command = "import os,pathlib,time; gate=pathlib.Path(os.environ['RUN_DIR']).parents[1]/'release.flag'; " + "\nwhile not gate.exists(): time.sleep(0.05)\n" + "pathlib.Path(os.environ['OUTPUT_ROOT'],'result.txt').write_text(pathlib.Path(os.environ['DATA_ROOT'],'fixed.txt').read_text())"
            deadline = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=45)).isoformat()
            args = self.args("run", "--input", f"fixed={source}", "--deadline", deadline, "--", "python", "-c", command)
            args.repo = str(tree)
            records.append(r.run(args))
            r.git(self.repo, "worktree", "remove", "--force", str(tree))
        (root / "release.flag").touch()
        until = time.monotonic() + 35
        while time.monotonic() < until:
            records = [r.read_json(Path(item["code_dir"]).parent / "run.json") for item in records]
            if all(item["status"] in {"succeeded", "failed", "cancelled"} for item in records):
                break
            time.sleep(0.2)
        self.assertEqual([item["status"] for item in records], ["succeeded", "succeeded"])
        self.assertEqual(records[0]["environment_dir"], records[1]["environment_dir"])
        self.assertEqual(records[0]["inputs"], records[1]["inputs"])
        self.assertNotEqual(records[0]["artifacts"][0]["path"], records[1]["artifacts"][0]["path"])
        for item in records:
            self.assertEqual(Path(item["artifacts"][0]["path"]).read_text(), "fixed input")

    @unittest.skipUnless(os.environ.get("RESEARCH_NATIVE_TEST") == "1", "Set RESEARCH_NATIVE_TEST=1 on a real logged-in supported OS")
    def test_native_job_survives_deleted_worktree_with_imports_and_subprocess(self):
        self.setup()
        worktree = self.base / "disposable-worktree"
        r.git(self.repo, "worktree", "add", "--quiet", "--detach", str(worktree))
        args = self.args("run", "--", "python", "-c", "import time,os,pathlib,subprocess,sys; time.sleep(2); pathlib.Path('fixed_module.py').write_text('value=42'); import fixed_module; assert fixed_module.value==42; assert pathlib.Path('README.md').is_file(); subprocess.run([sys.executable,'-c',\"import os,pathlib; pathlib.Path(os.environ['OUTPUT_ROOT'],'result.txt').write_text('durable')\"],check=True)")
        args.repo = str(worktree)
        record = r.run(args)
        r.git(self.repo, "worktree", "remove", "--force", str(worktree))
        path = Path(record["code_dir"]).parent / "run.json"
        until = time.monotonic() + 30
        while time.monotonic() < until:
            record = r.read_json(path)
            if record["status"] in {"succeeded", "failed", "cancelled"}:
                break
            time.sleep(0.2)
        self.assertEqual(record["status"], "succeeded", record)
        self.assertEqual(Path(record["artifacts"][0]["path"]).read_text(), "durable")
        self.assertFalse(worktree.exists())
        r.worker(path)
        self.assertEqual(r.read_json(path)["attempts"], 1)


if __name__ == "__main__":
    unittest.main()
