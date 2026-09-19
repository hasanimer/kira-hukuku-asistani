"""Regression checks for mixed issues, traceable sources and fiction boundaries."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import scenarios


class ScenarioTests(unittest.TestCase):
    def test_all_references_resolve_with_limits(self):
        rows = scenarios.resolve(scenarios.load_catalog(ROOT), ROOT)
        for row in rows:
            self.assertTrue(row['fictional'])
            self.assertTrue(row['coverage'])
            for source in row['decisions']:
                self.assertTrue(source['text_sha256'])
                self.assertTrue(source['source_url'])
                self.assertTrue(source['research_notes'])

    def test_mixed_dispute_preserves_both_topics(self):
        rows = scenarios.search(scenarios.load_catalog(ROOT), 'RUTUBET DEPOZİTO')
        ids = {row['id'] for row in rows}
        self.assertTrue({'K2', 'K6'}.issubset(ids))

    def test_no_match_does_not_invent_source(self):
        self.assertEqual(scenarios.search(scenarios.load_catalog(ROOT), 'xyz-nonexistent'), [])
        with self.assertRaises(ValueError):
            scenarios.search(scenarios.load_catalog(ROOT), '   ')

    def test_broken_reference_fails(self):
        rows = copy.deepcopy(scenarios.load_catalog(ROOT)[:1])
        rows[0]['decision_ids'] = ['missing-decision']
        with self.assertRaisesRegex(ValueError, 'Missing source'):
            scenarios.resolve(rows, ROOT)

    def test_cli_portable_and_unknown_id_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/scenarios.py'),
                                   'show', 'k6'], cwd=directory, capture_output=True,
                                  encoding='utf-8')
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads(proc.stdout)
            self.assertTrue(result['fictional'])
            self.assertEqual(result['scenarios'][0]['id'], 'K6')
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/scenarios.py'),
                                   'show', 'K999'], cwd=directory, capture_output=True)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(proc.stdout, b'')


if __name__ == '__main__':
    unittest.main()
