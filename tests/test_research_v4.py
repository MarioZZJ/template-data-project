"""Client boundary checks; no platform writes, commits or paid jobs are performed."""
import contextlib
import json
import locale
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from test_research_runtime import r, SCRIPT


PROJECT = "00000000-0000-0000-0000-000000000101"
ISSUE = "00000000-0000-0000-0000-000000000102"
AGENT = "00000000-0000-0000-0000-000000000103"
SOURCE = "00000000-0000-0000-0000-000000000104"


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="research-v4-")
        self.base = Path(self.tmp.name)
        self.repo = self.base / "checkout"
        subprocess.run(["git", "clone", "--quiet", "--shared", str(SCRIPT.parents[1]), str(self.repo)], check=True)
        r.git(self.repo, "remote", "set-url", "origin", "https://example.test/research/client-v4.git")
        self.assets = self.base / "assets"
        self.env = patch.dict(os.environ, {key: value for key, value in os.environ.items()
                                         if key not in {"RESEARCHD_SOCKET", "MULTICA_ISSUE_ID", "MULTICA_AGENT_ID", "MULTICA_TASK_ID"}}, clear=True)
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def args(self, *argv):
        return r.parser().parse_args(["--repo", str(self.repo), "--assets-home", str(self.assets), *argv])

    def setup_v4(self):
        with patch.object(r, "service_request", side_effect=r.ServiceUnavailable("offline")):
            return r.setup(self.args("setup", "--stdlib", "--harness", "v4", "--project-id", PROJECT,
                                     "--service-socket", str(self.base / "service.sock"), "--executor-agent-id", AGENT))

    def run_args(self, *extra):
        return self.args("run", "--issue-id", ISSUE, "--entry", "analysis", "--request-key", "stable-request-one",
                         "--receiver-agent-id", AGENT, "--source-run-id", SOURCE, *extra,
                         "--", "python", "src/analysis.py")

    def test_unavailable_setup_registers_v4_without_starting_anything(self):
        result = self.setup_v4()
        self.assertFalse(result["service_available"])
        self.assertEqual(result["harness_version"], 4)
        _, entry = r.project_config(self.args("context", "--issue-id", ISSUE))
        self.assertEqual(entry["project_id"], PROJECT)
        self.assertEqual(entry["executor_agent_ids"], [AGENT])
        self.assertEqual(list((Path(result["asset_root"]) / "runs").iterdir()), [])

    def test_unavailable_submit_never_falls_back_to_native_execution(self):
        result = self.setup_v4()
        with patch.object(r, "service_request", side_effect=r.ServiceUnavailable("unknown")), patch.object(r, "legacy_run") as native:
            with self.assertRaises(r.ServiceUnavailable):
                r.run(self.run_args())
            native.assert_not_called()
        self.assertEqual(list((Path(result["asset_root"]) / "runs").iterdir()), [])

    def test_v4_rejects_foreground_and_unregistered_allowance(self):
        self.setup_v4()
        with patch.object(r, "service_request") as service:
            for extra in (("--foreground",), ("--budget-json", '{"money":100}'), ("--attempt-limit", "2")):
                with self.assertRaises(ValueError):
                    r.run(self.run_args(*extra))
            service.assert_not_called()

    def test_fixed_intent_and_source_are_sent_without_credentials(self):
        self.setup_v4()
        receipt = {"accepted": True, "job_id": "job-one", "request_key": "stable-request-one"}
        with patch.object(r, "service_request", return_value=receipt) as service:
            self.assertEqual(r.run(self.run_args()), receipt)
        operation, payload = service.call_args.args[2:]
        self.assertEqual(operation, "submit")
        self.assertEqual(payload["source_run_id"], SOURCE)
        self.assertEqual(payload["receiver_agent_id"], AGENT)
        self.assertEqual(payload["request_key"], "stable-request-one")
        self.assertEqual(payload["code_ref"]["identity"], r.git(self.repo, "rev-parse", "HEAD"))
        self.assertNotIn("token", json.dumps(payload).lower())

    def test_unaccepted_service_reply_is_not_reported_as_a_job(self):
        self.setup_v4()
        with patch.object(r, "service_request", return_value={"accepted": False, "job_id": "job-one"}):
            with self.assertRaises(r.ServiceUnavailable):
                r.run(self.run_args())

    def test_dirty_actual_code_cannot_be_submitted_with_old_head(self):
        self.setup_v4()
        (self.repo / "README.md").write_text("new actual code context")
        with patch.object(r, "service_request") as service:
            with self.assertRaises(ValueError):
                r.run(self.run_args())
            service.assert_not_called()

    def test_context_fallback_reads_full_edited_threads_and_filters_agents(self):
        self.setup_v4()
        calls = []
        edited = {"id": "comment-one", "content": "Updated permission", "created_at": "old", "updated_at": "new", "revision": 4}

        def native(args, entry, *argv):
            calls.append(argv)
            if argv[:2] == ("issue", "get"):
                return {"id": ISSUE, "project_id": PROJECT, "description": "Current contract", "revision": 5}
            if argv[:3] == ("issue", "comment", "list"):
                return [edited]
            if argv[:2] == ("issue", "runs"):
                return []
            if argv[:2] == ("agent", "list"):
                return [{"id": AGENT, "name": "Research executor", "api_key": "PRIVATE"},
                        {"id": "ops-member", "name": "Operations", "api_key": "PRIVATE"}]
            raise AssertionError(argv)

        before = (self.assets / "projects.json").read_bytes()
        with patch.object(r, "service_request", side_effect=r.ServiceUnavailable("offline")), patch.object(r, "cli_json", side_effect=native):
            result = r.context(self.args("context", "--issue-id", ISSUE))
        self.assertEqual(result["comments"], [edited])
        self.assertEqual(result["source"], "multica-cli")
        self.assertEqual(result["eligible_executors"], [{"id": AGENT, "name": "Research executor"}])
        self.assertIn(("issue", "comment", "list", ISSUE, "--full"), calls)
        self.assertNotIn("PRIVATE", json.dumps(result))
        self.assertEqual((self.assets / "projects.json").read_bytes(), before)

    def test_context_parent_contracts_and_edits_are_included(self):
        self.setup_v4()

        def native(args, entry, *argv):
            if argv[:2] == ("issue", "get"):
                key = argv[2]
                return {"id": key, "project_id": PROJECT, "parent_issue_id": {ISSUE: "phase", "phase": "control"}.get(key)}
            if argv[:3] == ("issue", "comment", "list"):
                return [{"id": argv[3] + "-comment", "content": "Current edited contract", "revision": 3}]
            return []

        with patch.object(r, "service_request", return_value={"jobs": []}), patch.object(r, "cli_json", side_effect=native):
            result = r.context(self.args("context", "--issue-id", ISSUE))
        self.assertEqual([parent["issue"]["id"] for parent in result["parents"]], ["phase", "control"])
        self.assertTrue(all(parent["comments"][0]["revision"] == 3 for parent in result["parents"]))

    def test_context_rejects_cross_project_issue(self):
        self.setup_v4()
        with patch.object(r, "service_request", return_value={}), patch.object(r, "cli_json", return_value={"id": ISSUE, "project_id": "another-project"}):
            with self.assertRaises(ValueError):
                r.context(self.args("context", "--issue-id", ISSUE))

    def test_context_reads_full_ancestor_chain_or_explicitly_rejects_it(self):
        self.setup_v4()
        chains = []
        for count in (3, 16, 17):
            identifiers = [ISSUE, *[f"ancestor-{number}" for number in range(count)]]
            links = dict(zip(identifiers, identifiers[1:]))
            chains.append((str(count), links, count, None if count <= 16 else "exceeds 16"))
        chains.append(("cycle", {ISSUE: "phase", "phase": "control", "control": "phase"}, None, "cycle"))
        for name, links, count, failure in chains:
            with self.subTest(chain=name):
                def native(args, entry, *argv):
                    if argv[:2] == ("issue", "get"):
                        return {"id": argv[2], "project_id": PROJECT, "parent_issue_id": links.get(argv[2])}
                    if argv[:3] == ("issue", "comment", "list"):
                        return [{"id": argv[3] + "-comment", "content": "Current authorization", "revision": 4}]
                    return []

                with patch.object(r, "service_request", return_value={"jobs": []}), patch.object(r, "cli_json", side_effect=native):
                    if failure:
                        with self.assertRaisesRegex(RuntimeError, failure):
                            r.context(self.args("context", "--issue-id", ISSUE))
                    else:
                        result = r.context(self.args("context", "--issue-id", ISSUE))
                        self.assertEqual(len(result["parents"]), count)
                        self.assertEqual(result["parents"][-1]["issue"]["id"], f"ancestor-{count - 1}")
                        self.assertEqual(result["parents"][-1]["comments"][0]["revision"], 4)

    def test_service_context_normalizes_project_members_and_parent_contracts(self):
        self.setup_v4()
        remote = {"issue": {"id": ISSUE, "project_id": PROJECT}, "comments": [],
                  "context_ref": "context-read-one", "contract_context": {"source_run_id": SOURCE},
                  "ancestors": [{"issue": {"id": "phase"}, "comments": []}],
                  "task_runs": [{"id": SOURCE, "status": "running"}, {"id": "old", "status": "completed"}],
                  "available_agents": [{"id": AGENT, "name": "Executor", "runtime_id": "runtime", "token": "PRIVATE"},
                                       {"id": "ops", "name": "Operations"}]}
        with patch.object(r, "service_request", return_value=remote), patch.object(r, "cli_json") as cli:
            result = r.context(self.args("context", "--issue-id", ISSUE, "--source-run-id", SOURCE))
        self.assertEqual(result["source"], "researchd")
        self.assertEqual(result["context_ref"], "context-read-one")
        self.assertEqual(len(result["parents"]), 1)
        self.assertEqual(result["active_runs"], [{"id": SOURCE, "status": "running"}])
        self.assertEqual(result["eligible_executors"], [{"id": AGENT, "name": "Executor", "runtime_id": "runtime"}])
        self.assertNotIn("PRIVATE", json.dumps(result))
        cli.assert_not_called()

    def test_context_exposes_only_service_client_entrypoint_fields_without_execution(self):
        self.setup_v4()
        entrypoint = {"path": str(self.base / "release" / "research.py"), "sha256": "a" * 64,
                      "usage": "Use this registered client for the current C trial"}
        remote = {"issue": {"id": ISSUE, "project_id": PROJECT}, "comments": [],
                  "context_ref": "actual-service-context", "client_entrypoint": dict(entrypoint, token="PRIVATE", extra={"secret": "PRIVATE"}),
                  "unexpected_platform_field": "PRIVATE"}
        with patch.object(r, "service_request", return_value=remote), patch.object(r, "cli_json") as cli, \
                patch.object(r, "publish") as publish, patch.object(r, "run") as run:
            result = r.context(self.args("context", "--issue-id", ISSUE, "--source-run-id", SOURCE))
        self.assertEqual(result["source"], "researchd")
        self.assertEqual(result["context_ref"], "actual-service-context")
        self.assertEqual(result["client_entrypoint"], entrypoint)
        self.assertIsNone(result["service_context"])
        self.assertNotIn("PRIVATE", json.dumps(result))
        cli.assert_not_called()
        publish.assert_not_called()
        run.assert_not_called()

    def test_context_omits_malformed_client_entrypoint_without_changing_other_fields(self):
        self.setup_v4()
        for entrypoint in (None, "arbitrary program", {"path": {"secret": "PRIVATE"}, "sha256": "a" * 64, "usage": "info"},
                           {"path": "/client.py", "sha256": "a" * 64}):
            remote = {"issue": {"id": ISSUE, "project_id": PROJECT}, "comments": [],
                      "context_ref": "actual-service-context", "client_entrypoint": entrypoint}
            with self.subTest(entrypoint=entrypoint), patch.object(r, "service_request", return_value=remote):
                result = r.context(self.args("context", "--issue-id", ISSUE))
            self.assertNotIn("client_entrypoint", result)
            self.assertEqual(result["context_ref"], "actual-service-context")
            self.assertEqual(result["source"], "researchd")

    def test_checkpoint_preserves_unrelated_index_and_labels_patch(self):
        r.setup(self.args("setup", "--stdlib"))
        (self.repo / "README.md").write_text("selected change\n")
        (self.repo / "AGENTS.md").write_text("someone else's staged change\n")
        r.git(self.repo, "add", "--", "AGENTS.md")
        index_before = r.git(self.repo, "diff", "--cached", "--binary")
        head_before = r.git(self.repo, "rev-parse", "HEAD")
        result = r.checkpoint(self.args("checkpoint", "--file", "README.md"))
        self.assertFalse(result["committed"])
        self.assertEqual(result["kind"], "patch")
        self.assertEqual([item["path"] for item in result["files"]], ["README.md"])
        self.assertEqual(Path(result["files"][0]["content_path"]).read_text(), "selected change\n")
        self.assertEqual(r.git(self.repo, "diff", "--cached", "--binary"), index_before)
        self.assertEqual(r.git(self.repo, "rev-parse", "HEAD"), head_before)

    def test_command_output_preserves_utf8_under_a_legacy_console_locale(self):
        message = "研究执行入口：保留中文差异"
        command = [sys.executable, "-c", "import sys; sys.stdout.buffer.write(" + repr(message.encode("utf-8")) +
                   "); sys.stderr.buffer.write(b'\\x81')"]
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(locale, "getpreferredencoding", return_value="cp1252"))
            if hasattr(locale, "getencoding"):
                stack.enter_context(patch.object(locale, "getencoding", return_value="cp1252"))
            self.assertEqual(r.call(command), message)
            raw = b"non-utf8-path-\xff"
            output = r.call([sys.executable, "-c", "import sys; sys.stdout.buffer.write(" + repr(raw) + ")"])
            self.assertEqual(output.encode("utf-8", errors="surrogateescape"), raw)

    def test_checkpoint_rejects_broad_and_credential_paths(self):
        r.setup(self.args("setup", "--stdlib"))
        for value in (".", "../outside", ".git/config", ".env", "missing-file"):
            with self.subTest(value=value), self.assertRaises((ValueError, RuntimeError)):
                r.checkpoint(self.args("checkpoint", "--file", value))

    def test_commit_requires_reviewed_message_and_never_guesses_attribution(self):
        r.setup(self.args("setup", "--stdlib"))
        with patch.object(r, "call", wraps=r.call) as commands:
            with self.assertRaises(ValueError):
                r.checkpoint(self.args("checkpoint", "--file", "README.md", "--commit"))
        self.assertFalse(any("commit" in item.args[0] or "push" in item.args[0] for item in commands.call_args_list))

    def test_v4_delivery_records_actual_saved_code_and_refuses_dirty_code(self):
        setup = self.setup_v4()
        artifact = Path(setup["asset_root"]) / "inputs" / "result.txt"
        artifact.write_text("Complete result")
        args = self.args("deliver", "--issue-id", ISSUE, "--artifact", str(artifact), "--check", "coverage",
                         "--scope-complete", "--research-impact", "Supports the registered comparison", "--context-ref", "context-read-one")
        result = r.deliver(args)
        self.assertEqual(result["record"]["code_ref"], {"kind": "git_commit", "identity": r.git(self.repo, "rev-parse", "HEAD")})
        self.assertEqual(result["record"]["context_ref"], "context-read-one")
        (self.repo / "README.md").write_text("Unsaved research code")
        with self.assertRaises(ValueError):
            r.deliver(args)

    def test_v4_requires_context_receipt_and_review_finalization_refreshes_only_contract_reference(self):
        setup = self.setup_v4()
        artifact = Path(setup["asset_root"]) / "inputs" / "result.txt"
        artifact.write_text("Reviewed result")
        args = self.args("deliver", "--issue-id", ISSUE, "--artifact", str(artifact), "--check", "coverage",
                         "--scope-complete", "--research-impact", "Scoped finding", "--draft", "--review-required")
        with self.assertRaisesRegex(ValueError, "context-ref"):
            r.deliver(args)
        args.context_ref = "first-source-context"
        draft = r.deliver(args)
        final_args = self.args("deliver", "--issue-id", ISSUE, "--finalize", draft["delivery_path"],
                               "--review-evidence", SOURCE, "--issue-revision", "10", "--context-ref", "final-source-context")
        final = r.deliver(final_args)
        self.assertEqual(final["record"]["context_ref"], "final-source-context")
        self.assertEqual(final["record"]["delivery_id"], draft["record"]["delivery_id"])
        self.assertEqual(final["record"]["artifacts"], draft["record"]["artifacts"])
        self.assertEqual(r.read_json(draft["delivery_path"])["context_ref"], "first-source-context")

    def test_delivery_registration_does_not_create_or_post_another_record(self):
        setup = self.setup_v4()
        directory = Path(setup["asset_root"]) / "deliveries"
        with patch.object(r, "service_request", return_value={"state": "pending"}) as service:
            result = r.deliver(self.args("deliver", "--issue-id", ISSUE, "--submit-comment-id", SOURCE))
        self.assertEqual(result["operation"], "register_delivery")
        self.assertEqual(service.call_args.args[2:], ("deliver", {"project_id": PROJECT, "issue_id": ISSUE, "comment_id": SOURCE}))
        self.assertEqual(list(directory.iterdir()), [])

    def test_consumption_requires_stable_evidence_and_remains_distinct_from_delivery(self):
        setup = self.setup_v4()
        evidence = Path(setup["asset_root"]) / "result-note.txt"
        evidence.write_text("Result supports the scoped comparison")
        args = self.args("deliver", "--issue-id", ISSUE, "--consume-event", "event-one", "--source-run-id", SOURCE,
                         "--evidence-path", str(evidence), "--judgment", "Scoped comparison supported", "--next-action", "Prepare final delivery")
        with patch.object(r, "service_request", return_value={"state": "consumed"}) as service:
            result = r.deliver(args)
        self.assertEqual(result["operation"], "consume_result")
        self.assertEqual(service.call_args.args[2], "consume")
        self.assertEqual(service.call_args.args[3]["source_run_id"], SOURCE)
        self.assertEqual(list((Path(setup["asset_root"]) / "deliveries").iterdir()), [])
        args.evidence_path = str(self.repo / "README.md")
        with self.assertRaises(ValueError):
            r.deliver(args)

    def test_status_does_not_recover_v4_jobs_implicitly(self):
        self.setup_v4()
        with patch.object(r, "service_request", side_effect=r.ServiceUnavailable("offline")), patch.object(r, "reconcile_run") as reconcile:
            result = r.status(self.args("status", "--issue-id", ISSUE))
            self.assertFalse(result["service_available"])
            reconcile.assert_not_called()
            with self.assertRaises(ValueError):
                r.status(self.args("status", "--reconcile"))

    @unittest.skipUnless(hasattr(socket, "AF_UNIX") and os.name != "nt", "Unix socket client is first validated on Linux")
    def test_socket_protocol_preserves_newline_framing_and_masks_server_errors(self):
        path = str(self.base / "protocol.sock")
        for reply, rejected in (({"ok": True, "result": {"supported": True}}, False),
                                ({"ok": False, "error": {"code": "policy_denied", "message": "PRIVATE SECRET"}}, True)):
            with self.subTest(rejected=rejected), socket.socket(socket.AF_UNIX) as server:
                server.bind(path)
                server.listen(1)
                received = []

                def respond():
                    with server.accept()[0] as connection:
                        raw = b""
                        while not raw.endswith(b"\n"):
                            raw += connection.recv(1024)
                        received.append(json.loads(raw))
                        connection.sendall(json.dumps(reply).encode() + b"\n")

                thread = threading.Thread(target=respond)
                thread.start()
                if rejected:
                    with self.assertRaises(r.ServiceRejected) as error:
                        r.service_request(self.args("context"), {"service_socket": path}, "context", {"issue_id": ISSUE})
                    self.assertNotIn("PRIVATE", str(error.exception))
                else:
                    self.assertEqual(r.service_request(self.args("context"), {"service_socket": path}, "context", {"issue_id": ISSUE}), {"supported": True})
                thread.join(timeout=2)
                self.assertFalse(thread.is_alive())
                self.assertEqual(received, [{"operation": "context", "payload": {"issue_id": ISSUE}}])
            Path(path).unlink()


if __name__ == "__main__":
    unittest.main()
