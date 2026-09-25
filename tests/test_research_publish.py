"""Pinned publisher seam checks; never call Multica or publish a real comment."""
import json
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import test_research_v4 as v4

r, PROJECT, ISSUE, AGENT, SOURCE = v4.r, v4.PROJECT, v4.ISSUE, v4.AGENT, v4.SOURCE


class PublishTests(unittest.TestCase):
    setUp = v4.ClientTests.setUp
    tearDown = v4.ClientTests.tearDown
    args = v4.ClientTests.args
    setup_v4 = v4.ClientTests.setup_v4

    def prepare_publisher(self):
        setup = self.setup_v4()
        self.root = Path(setup['asset_root'])
        self.helper = self.base / 'deployer-release' / 'publish_delivery.py'
        self.helper.parent.mkdir()
        # A standalone fake of the registered command protocol, not a second
        # implementation of publication, revision checks or service behavior.
        self.helper.write_text('''import argparse, hashlib, json, os
from pathlib import Path
p = argparse.ArgumentParser()
for key in ('record', 'issue-id', 'project-id', 'socket', 'multica-cwd', 'summary', 'parent'):
    p.add_argument('--' + key)
a = p.parse_args()
raw = Path(a.record).read_bytes()
print(json.dumps({'state': 'registered', 'record_sha256': hashlib.sha256(raw).hexdigest(),
 'source_run_id': os.environ['MULTICA_TASK_ID'], 'agent_id': os.environ['MULTICA_AGENT_ID'],
 'issue_id': a.issue_id, 'project_id': a.project_id, 'record_fields_preserved': True,
 'observed_record_hex': raw.hex(), 'observed_socket': a.socket, 'observed_cwd': a.multica_cwd,
 'observed_summary': a.summary, 'observed_parent': a.parent}))
''', encoding='utf-8')
        self.checksum = r.digest(self.helper)
        args = self.args('setup', '--stdlib', '--publisher-helper', str(self.helper),
                         '--publisher-sha256', self.checksum, '--multica-cwd', str(self.base))
        with patch.object(r, 'service_request', side_effect=r.ServiceUnavailable('offline')):
            r.setup(args)
        self.record_path = self.root / 'deliveries/research-delivery-example.json'
        self.record = {'schema': 'research-delivery/v1', 'delivery_id': 'research-delivery-example', 'issue_id': ISSUE,
                       'context_ref': 'actual-context-receipt', 'issue_revision': 12,
                       'artifacts': [{'path': 'original', 'sha256': 'original-hash'}],
                       'code_ref': {'identity': 'actual-version'}, 'research_impact': '实际研究发现'}
        self.raw = ('\n' + json.dumps(self.record, ensure_ascii=False, indent=3) + '\n').encode('utf-8')
        self.record_path.write_bytes(self.raw)
        return self.args('publish', '--record', str(self.record_path), '--issue-id', ISSUE, '--summary', '实际发现及下一动作')

    def identity(self, **extra):
        return patch.dict(os.environ, {'MULTICA_TOKEN': 'mat_fixture_not_real', 'MULTICA_TASK_ID': SOURCE,
                                      'MULTICA_AGENT_ID': AGENT, 'MULTICA_ISSUE_ID': ISSUE, **extra})

    def test_setup_requires_explicit_path_and_digest_and_rejects_task_registration(self):
        for argv in [('setup', '--stdlib', '--publisher-helper', '/not-registered'),
                     ('setup', '--stdlib', '--publisher-sha256', 'f' * 64)]:
            with self.assertRaisesRegex(ValueError, 'requires both'):
                r.setup(self.args(*argv))
        with self.identity(), self.assertRaisesRegex(ValueError, 'deployer'):
            r.setup(self.args('setup', '--publisher-helper', '/not-registered', '--publisher-sha256', 'f' * 64))
        self.assertFalse((self.assets / 'projects.json').exists())

    def test_registration_pins_actual_release_outside_checkout(self):
        self.prepare_publisher()
        _, entry = r.project_config(self.args('context'))
        self.assertEqual(entry['delivery_publisher'], {'protocol': 'research-delivery-publication/v1',
                                                      'path': str(self.helper), 'sha256': self.checksum})
        with self.assertRaisesRegex(ValueError, 'does not match'):
            r.publisher_registration(str(self.helper), '0' * 64, self.repo)
        checkout_file = self.repo / 'README.md'
        with self.assertRaisesRegex(ValueError, 'outside'):
            r.publisher_registration(str(checkout_file), r.digest(checkout_file), self.repo)

    @unittest.skipUnless(os.name == 'posix', 'Publisher requires POSIX; ordinary runtime tests run on all platforms')
    def test_real_helper_invocation_preserves_bytes_and_uses_only_registered_destinations(self):
        args = self.prepare_publisher()
        args.parent = SOURCE
        with self.identity(RESEARCHD_SOCKET='/untrusted-text.sock', MULTICA_CLI_CWD='/untrusted-text',
                           PYTHONPATH='/untrusted-python-module'):
            result = r.publish(args)['result']
        self.assertEqual(bytes.fromhex(result['observed_record_hex']), self.raw)
        self.assertEqual(result['observed_socket'], str(self.base / 'service.sock'))
        self.assertEqual(result['observed_cwd'], str(self.base))
        self.assertEqual(result['observed_parent'], SOURCE)
        self.assertEqual(result['observed_summary'], '实际发现及下一动作')
        self.assertEqual(self.record_path.read_bytes(), self.raw)

    @unittest.skipUnless(os.name == 'posix', 'Publisher requires POSIX')
    def test_missing_registration_and_drift_never_execute_a_helper(self):
        self.setup_v4()
        args = self.args('publish', '--record', '/none', '--issue-id', ISSUE, '--summary', 'Result')
        with patch.object(r, 'call', wraps=r.call), self.assertRaisesRegex(ValueError, 'deployer-registered'):
            r.publish(args)
        # New isolated fixture for the registered case.
        self.prepare_publisher()
        self.helper.write_text('raise RuntimeError("changed release")')
        with self.identity(), self.assertRaisesRegex(ValueError, 'does not match'):
            r.publish(args)

    @unittest.skipUnless(os.name == 'posix', 'Publisher requires POSIX')
    def test_publish_requires_current_task_identity_and_matching_issue(self):
        args = self.prepare_publisher()
        with self.assertRaisesRegex(ValueError, 'task-scoped'):
            r.publish(args)
        with self.identity(MULTICA_ISSUE_ID=SOURCE), self.assertRaisesRegex(ValueError, 'differs'):
            r.publish(args)

    @unittest.skipUnless(os.name == 'posix', 'Publisher requires POSIX')
    def test_record_must_be_the_canonical_project_original(self):
        args = self.prepare_publisher()
        unrelated = self.base / self.record_path.name
        unrelated.write_bytes(self.raw)
        with self.identity():
            args.record = str(unrelated)
            with self.assertRaisesRegex(ValueError, 'original delivery'):
                r.publish(args)
            args.record = str(self.record_path)
            self.record_path.write_text(json.dumps(dict(self.record, delivery_id='another-file')))
            with self.assertRaisesRegex(ValueError, 'canonical'):
                r.publish(args)

    @unittest.skipUnless(os.name == 'posix', 'Publisher requires POSIX')
    def test_unknown_helper_outcome_is_not_retried_and_does_not_rebuild_record(self):
        args = self.prepare_publisher()
        _, entry = r.project_config(args)
        # Isolate invocation from repository discovery so call count means helper calls.
        with patch.object(r, 'project_config', return_value=(self.repo, entry)), self.identity(), \
                patch.object(r.subprocess, 'run', side_effect=subprocess.TimeoutExpired('publisher', 360)) as invoke:
            with self.assertRaisesRegex(r.ServiceUnavailable, 'unknown.*do not repost'):
                r.publish(args)
        self.assertEqual(invoke.call_count, 1)
        argv = invoke.call_args.args[0]
        self.assertEqual(argv[1:3], ['-I', str(self.helper)])
        self.assertNotIn('mat_fixture_not_real', repr(argv))
        self.assertEqual(self.record_path.read_bytes(), self.raw)

    def test_deliver_points_to_registered_publisher_without_invoking_it(self):
        self.prepare_publisher()
        artifact = self.root / 'inputs' / 'result.txt'
        artifact.write_text('Actual full result', encoding='utf-8')
        args = self.args('deliver', '--issue-id', ISSUE, '--artifact', str(artifact), '--check', 'coverage',
                         '--scope-complete', '--research-impact', 'Scoped finding', '--context-ref', 'actual-context',
                         '--issue-revision', '12')
        with patch.object(r, 'publish') as publish, patch.object(r, 'service_request') as service:
            result = r.deliver(args)
        self.assertIn('publish --record', result['next_action'])
        self.assertEqual(r.read_json(result['delivery_path']), result['record'])
        publish.assert_not_called()
        service.assert_not_called()

    def test_non_posix_publish_rejects_before_registry_or_helper_access(self):
        args = self.args('publish', '--record', '/none', '--issue-id', ISSUE, '--summary', 'Result')
        with patch.object(r.os, 'name', 'nt'), patch.object(r, 'project_config') as config:
            with self.assertRaisesRegex(r.ServiceUnavailable, 'POSIX'):
                r.publish(args)
            config.assert_not_called()


if __name__ == '__main__':
    unittest.main()
